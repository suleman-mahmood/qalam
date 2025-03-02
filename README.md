#### Qalam

Install [poetry](https://python-poetry.org/docs/) first
To get started, always start a shell using: `poetry shell`
Install dependencies: `poetry install`

Run the tree-sitter script: `python qalam/static-analyser.py`
When prompted enter: `./qalam`

#### Tools
- CLI, choosing options, editing blob of text, accept / regenerate stuff
- Python
- Model: DeepSeek r1 or OpenAI

#### Step 1, Static Analysis
Codebase -> Statically analysed data

- Input codebase, outputs a file within the token limit
- Use treesitter to get python functions names from all the project files in  the targeted codebase
- Make one huge file for next step
	- Either treesitter creates relationship
	- Or choose a format for a file and store all the information inside it

#### Step 2, Embeddings
Vectorise data into db

- Vectorise the above file
- Store this in vector db, use pinecone db for simplicity

#### Step 3, Code Plan
User prompt + context -> Code plan

- User enters a prompt
- Prompt (User query) will be embedded and use it to query vector db to get retrieved context
- Construct system prompt from above step
- Send this to LLM
- LLM output's the code plan

#### Step 4, 1st user interaction
Code plan -> Code stubs

- Show the code plan on CLI
- User approves / regenerates (or edits) the plan
	- Regenerate
	- Approve
		- Construct a new system prompt
		- Code plan & new instructions will be sent to LLM
- We get stubs from LLM

#### Step 5, 2nd user interaction
Code stubs -> Code implementation

- Show the stubs on CLI
- User approves / regenerates (or edits) the plan
	- Regenerate
	- Approve
		- Construct a new system prompt
		- Stubs  & new instructions will be sent to LLM
- We get Code implementation from LLM
