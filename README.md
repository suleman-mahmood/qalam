#### Qalam

Install [poetry](https://python-poetry.org/docs/) first
To get started, always start a shell using: `poetry shell`
Install dependencies: `poetry install`

Run your custom llm: `python -m qalam.main`


#### Tools
- CLI: choosing options, editing blob of text, accept / regenerate stuff
- Python
- Model: DeepSeek r1 or OpenAI

#### Step 1, Static Analysis
Codebase -> Statically analysed data

- Input codebase, outputs a list of structured data
- Use treesitter to get python classes & functions names for each file

#### Step 2, Generate embeddings
Vectorise data into db

- Split data into documents
- Store this in vector db (pinecone)

#### Step 3, Code Plan & stubs
User prompt + context -> Code plan

- User enters a prompt
- Prompt (User query) will be embedded and use it to query vector db to get context
- Construct system prompt  and send it to LLM
- LLM output's the code plan
- Edit / regenerate the code plan until satisfied

#### Step 4, Code implementation
Code plan & stubs -> Code implementation

- Feed the LLM's output from last step and use it to create embeddings and get context from the whole codebase
- Construct system prompt  and send it to LLM
- LLM output's the code implementation
- Edit / regenerate the code implementation satisfied

#### Logging
- Save sequence of user inputs and llm responses in a file

#### Use cases
- [x] Choose to generate stubs
- [x] Choose to generate code implementations from stubs provided
- [ ] Choose an option to write a function (route, db, workflow, controller) and give a prompt
- [ ] Choose an option to write a test case for a function (route, db, workflow, controller) and provide the code for the function

- User input is provided from a file, specific for each prompt

#### QA
- Test against the same input to 'Cursor'
