import json
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
from .models import CodeModification, CodeInstruction
from collections import defaultdict
from typing import List

class QueryProcessor:
    def __init__(
        self,
        openai_model: str = "gpt-4o",
        top_k: int = 10,
        query_prefix: str = "Instruct: Given a question or statement, retrieve code snippets that answer the question.\nQuery: "
    ):
        """
        Initialize the query processor.
        
        Args:
            openai_model: OpenAI model to use
            top_k: Number of similar chunks to retrieve
            query_prefix: Prefix to add to queries
        """
        self.logger = logging.getLogger(__name__)
        self.openai_model = openai_model
        self.top_k = top_k
        self.query_prefix = query_prefix
        self.client = OpenAI()

    def process(self, query: str, embedder: Any, db: Any) -> None:
        """
        Process a query against the codebase.
        
        Args:
            query: The query to process
            embedder: Embedder instance to compute embeddings
            db: DatabaseManager instance for retrieving chunks
        """
        self.logger.info(f"Processing query: {query}")

        # Compute query embedding and get similar chunks
        query_embedding = embedder.compute_embedding(query, self.query_prefix)
        chunks = db.get_similar_chunks(query_embedding, self.top_k)
        
        if not chunks:
            self.logger.warning("No relevant chunks found")
            return

        # Organize chunks by file
        project_files = {}
        for filename, _, _, code in chunks:
            project_files.setdefault(filename, []).append(code)

        # Get AST information for relevant files
        ast_map = self._build_ast_map(project_files.keys())

        # Preprocess the query to enhance it with context and code
        enhanced_query = self._preprocess_query(query, project_files)

        # Get and apply update instructions using enhanced query
        instructions = self._get_update_instructions(enhanced_query, project_files, ast_map)
        if instructions:
            self._apply_instructions(instructions)

    def _build_ast_map(self, filenames: List[str]) -> Dict[str, Any]:
        """Build AST map for the given files."""
        ast_map = {}
        for filename in filenames:
            try:
                from .tree_sitter_utils import get_ast_for_file
                ast_result = get_ast_for_file(filename)
                if "error" in ast_result:
                    self.logger.warning(f"AST error for {filename}: {ast_result['error']}")
                    ast_map[filename] = {}
                else:
                    ast_map[filename] = ast_result
            except Exception as e:
                self.logger.exception(f"Error processing AST for {filename}")
                ast_map[filename] = {}
        return ast_map

    def _get_update_instructions(
        self,
        query: str,
        project_files: Dict[str, List[str]],
        ast_map: Dict[str, Any]
    ) -> Optional[List[CodeInstruction]]:
        """Get update instructions from OpenAI."""
        prompt = self._build_prompt(query, project_files, ast_map)
        print(prompt)
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a coding assistant that returns structured code modifications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format=CodeModification,
            )
            if response.choices[0].message.refusal is not None:
                self.logger.warning(f"Model refused to make changes: {response.choices[0].message.refusal}")
                return None
            print(response.choices[0].message.parsed)
            return response.choices[0].message.parsed.instructions
            
        except Exception as e:
            self.logger.exception("Failed to get update instructions")
            return None

    def _build_prompt(
        self,
        query: str,
        project_files: Dict[str, List[str]],
        ast_map: Dict[str, Any]
    ) -> str:
        """Build the prompt for the OpenAI API."""
        docstring_instructions = (
            "We only have three types of code modification instructions:\n"
            "  1) 'update'\n"
            "  2) 'insert'\n"
            "  3) 'delete'\n\n"
            "However, the user might request more abstract operations like:\n"
            "  - \"Rename variable X to Y\"   -> Interpret as an 'update' that replaces X with Y.\n"
            "  - \"Move this function\"       -> Possibly a 'delete' from one location and an 'insert' into another.\n"
            "  - \"Convert function A to B\"  -> Could be a single 'update' or a combination of 'delete' + 'insert'.\n"
            "  - \"Refactor this code\"       -> Could involve multiple 'update', 'insert', or 'delete' steps.\n\n"
            "If multiple steps are needed, produce multiple instructions in the sequence that best accomplishes the task.\n"
            "Remember to handle edge cases—like references that need to change in other parts of the code—by\n"
            "suggesting corresponding updates or inserts/deletes in those files as well.\n\n"
            "All code snippets in 'replace' or 'write' fields should be complete and functional.\n"
            "Each 'find' field should match exactly what needs to be replaced, inserted around, or removed.\n"
            "If a 'convert' request implies removing old code and writing new code elsewhere,\n"
            "do so via 'delete' plus 'insert' instructions or a single 'update' if it's localized.\n\n"
            "If after analyzing the query you find no code modifications are necessary,\n"
        )
        return (
            f"Using the following project files and their AST mappings, "
            f"provide code modification instructions according to the query.\n\n"
            f"Project Files:\n{json.dumps(project_files, indent=2)}\n\n"
            f"AST Map:\n{json.dumps(ast_map, indent=2)}\n\n"
            f"Query: {query}\n\n"
            "Return a CodeModification object with instructions following these formats:\n"
            "1. For updates: Set type='update', filename, find=<exact code to replace>, replace=<new code>\n"
            "2. For inserts: Set type='insert', filename, find=<location marker>, write=<new code>\n"
            "3. For deletes: Set type='delete', filename, delete=<code to remove>\n\n"
            "Ensure all code snippets are complete and functional."
            "Analyze your suggested updates to ensure the code still runs and is functional."
            f"{docstring_instructions}"
            "If you rewrite a function ensure the old version is deleted and the new version is inserted."
        )
   
    @staticmethod
    def _flexible_pattern(text: str) -> str:
        """
        Create a regex pattern that matches the given text with flexible internal
        whitespace but preserves the exact indentation at the beginning of each line
        and the newline boundaries.
        """
        # Split the input text into individual lines
        lines = text.splitlines()
        pattern_lines = []
        
        for line in lines:
            # Match and capture the indentation and the rest of the content
            m = re.match(r'^(\s*)(.*)$', line)
            if m:
                indent, content = m.groups()
                # Split the content into tokens based on any whitespace
                tokens = re.split(r'\s+', content)
                tokens = [token for token in tokens if token]  # Remove any empty tokens
                
                # Build the pattern for this line:
                # - The indentation must match exactly.
                # - The remaining content is matched flexibly using \s+ between tokens.
                if tokens:
                    # Start with the exact indentation
                    pattern_line = re.escape(indent) + re.escape(tokens[0])
                    for token in tokens[1:]:
                        pattern_line += r'\s+' + re.escape(token)
                else:
                    # If there's no content (an empty line), match just the indentation
                    pattern_line = re.escape(indent)
                
                pattern_lines.append(pattern_line)
            else:
                # Fallback: escape the whole line if it doesn't match the expected format
                pattern_lines.append(re.escape(line))
        
        # Join the per-line patterns with a newline pattern that matches typical newline variations
        final_pattern = r'\r?\n'.join(pattern_lines)
        return final_pattern
    
    def _apply_instruction(self, instruction: CodeInstruction, content: str) -> str:
        """
        Apply a single instruction to the content.
        Uses a whitespace-tolerant matching approach for update, insert, and delete.
        """
        instr_type = instruction.type
        find = instruction.find
        replace = instruction.replace
        write_text = instruction.write

        # Build the flexible pattern only if 'find' is present
        if find:
            pattern_str = self._flexible_pattern(find)
            pattern = re.compile(pattern_str, re.MULTILINE | re.DOTALL)
        else:
            pattern = None

        # 1) Handle 'update'
        if instr_type == "update" and find and replace:
            if pattern:
                updated_content, num_subs = pattern.subn(replace, content)
                if num_subs == 0:
                    self.logger.warning(
                        f"No flexible matches found for 'update' instruction: {find}"
                    )
                return updated_content
            return content

        # 2) Handle 'insert' (inserting text right after the matched pattern)
        elif instr_type == "insert" and find and write_text:
            if pattern:
                match = pattern.search(content)
                if match:
                    pos = match.end()
                    return content[:pos] + "\n" + write_text + content[pos:]
                else:
                    self.logger.warning(
                        f"No flexible matches found for 'insert' instruction: {find}"
                    )
            return content

        # 3) Handle 'delete'
        elif instr_type == "delete" and find:
            if pattern:
                updated_content, num_subs = pattern.subn("", content)
                if num_subs == 0:
                    self.logger.warning(
                        f"No flexible matches found for 'delete' instruction: {find}"
                    )
                return updated_content
            return content

        # If none of the above matched or the instruction is incomplete, return content unmodified
        return content

    def _apply_instructions(self, instructions: List[CodeInstruction]) -> None:
        """
        Apply the instructions to the files in a single pass per file.
        This approach is more robust for handling multiple instructions against
        the same file and for dealing with whitespace/linebreak variations.
        """
        # Group instructions by filename
        instructions_by_file = defaultdict(list)
        for instr in instructions:
            if instr.filename:  # only handle instructions that have a valid filename
                instructions_by_file[instr.filename].append(instr)

        # Process each file once
        for filename, file_instructions in instructions_by_file.items():
            file_path = Path(filename)
            if not file_path.exists():
                self.logger.warning(f"File not found: {filename}")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Apply each instruction in order
                for instruction in file_instructions:
                    content = self._apply_instruction(instruction, content)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.logger.info(f"Updated {filename}")

            except Exception as e:
                self.logger.exception(f"Error updating {filename}: {e}")

    def _preprocess_query(self, query: str, project_files: Dict[str, List[str]]) -> str:
        """
        Enhance the user's query by first getting clear natural language instructions,
        including the relevant code context.
        
        Args:
            query: The original user query
            project_files: Dictionary of filenames to their code snippets
            
        Returns:
            Enhanced query with clear natural language instructions
        """
        # Format code snippets for the prompt
        code_context = ""
        for filename, snippets in project_files.items():
            code_context += f"\nFile: {filename}\n"
            code_context += "```\n"
            code_context += "\n".join(snippets)
            code_context += "\n```\n"

        preprocessing_prompt = (
            "You are an expert programmer. Given a user's request for code changes and "
            "the relevant code snippets, provide clear and specific natural language "
            "instructions for what needs to be modified. Break down complex changes into "
            "clear steps. Focus on being specific about what code needs to change and how.\n\n"
            
            f"Relevant Code:\n{code_context}\n"
            
            f"User Query: {query}\n\n"
            
            f"Ensure it is compabtible with our regex pattern parser:"

            "Provide clear, specific instructions for implementing these changes. "
            "Reference specific parts of the code in your instructions. "
            "Be precise about what needs to be modified, added, or removed."
            "Provide instructions in a format with Update, Insert, and Delete instructions."
            "You can show entire code updated if needed."
        )
        
        # Get natural language instructions from LLM
        response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=[ 
                {"role": "user", "content": preprocessing_prompt}
            ],
            temperature=0.7
        )
        
        enhanced_instructions = response.choices[0].message.content
        
        # Now build the final query with the enhanced instructions and code context
        final_query = (
            f"Original Request: {query}\n\n"
            f"Code Context:\n{code_context}\n"
            f"Detailed Instructions: {enhanced_instructions}\n\n"
            "Based on these instructions and the provided code, please provide the necessary code modifications."
        )
        
        return final_query