from qalam.static_analyser import StaticAnalyser

if __name__ == "__main__":
    static_analyser = StaticAnalyser()

    directory = input("Enter directory path to analyze: ")
    if directory == "-1":
        directory = "/Users/sulemanmahmood/Projects/mazlo/mazlo-backend"

    result = static_analyser.analyze_directory(directory)

    # Print results
    for file, data in result.items():
        print(f"\nFile: {file}")
        print(f"Classes: {data['classes']}")
        print(f"Functions: {data['functions']}")
        print(f"Imports: {data['imports']}")
        # print(f"Imported by: {data['imported_by']}")
