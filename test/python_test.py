# python_test.py

def become_radiology_technician():
    """Returns a list of steps to become a radiology technician."""
    steps = [
        "Earn a high school diploma.",
        "Take science and math courses to prepare for college.",
        "Obtain an associate degree from an accredited radiologic technology program.",
        "Pass the ARRT certification exam.",
        "Apply for Michigan state licensure through the Michigan Department of Licensing and Regulatory Affairs (LARA).",
        "Consider pursuing additional certifications or specializations."
    ]
    return steps

def become_pilot():
    """Returns a list of steps to become a pilot."""
    steps = [
        "Earn a high school diploma.",
        "Attend a flight school or obtain a degree in aviation.",
        "Get a private pilot license (PPL).",
        "Log sufficient flight hours.",
        "Obtain a commercial pilot license (CPL).",
        "Pass the Federal Aviation Administration (FAA) exams.",
        "Apply for jobs with airlines or other aviation companies."
    ]
    return steps

def become_superman():
    """Returns a humorous list of steps to become Superman."""
    steps = [
        "Be born on the planet Krypton.",
        "Survive the destruction of Krypton and be sent to Earth.",
        "Be raised by human parents with strong moral values.",
        "Discover your superpowers under Earth's yellow sun.",
        "Use your powers to fight for truth, justice, and the American way."
    ]
    return steps

def main():
    """Prints the steps to become a radiology technician, pilot, and Superman."""
    print("Steps to become a radiology technician:")
    for step in become_radiology_technician():
        print(step)

    print("Steps to become a pilot:")
    for step in become_pilot():
        print(step)

    print("Steps to become Superman:")
    for step in become_superman():
        print(step)

if __name__ == "__main__":
    main()
