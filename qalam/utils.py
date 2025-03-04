from qalam.static_analyser import PythonFileAnalysis


def parse_python_file_analysis_to_embedding_documents(
    analysis_filse: list[PythonFileAnalysis],
) -> list[str]:
    result: list[str] = []
    for f in analysis_filse:
        out = f"""
        File name with relative path: {f.file_path}
        {f"Defined classes: {f.classes}" if f.classes else "No classes defined"}
        {f"Defined functions: {f.functions}" if f.functions else "No functions defined"}
        {f"Imports used in file: {f.imports}" if f.imports else "No imports used in file"}
        """
        result.append(out)

    return result
