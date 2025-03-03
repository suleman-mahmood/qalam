from qalam.static_analyser import analyze_directory

if __name__ == "__main__":
    directory = input("Enter directory path to analyze: ")
    result = analyze_directory(directory)

    # Print results
    for file, data in result.items():
        print(f"\nFile: {file}")
        print(f"Classes: {data['classes']}")
        print(f"Functions: {data['functions']}")
        print(f"Imports: {data['imports']}")
        # print(f"Imported by: {data['imported_by']}")
