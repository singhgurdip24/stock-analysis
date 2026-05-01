from langchain_classic.output_parsers import StructuredOutputParser, ResponseSchema

response_schemas = [
    ResponseSchema(name="short_term", description="bullish, bearish or neutral"),
    ResponseSchema(name="medium_term", description="bullish, bearish or neutral"),
    ResponseSchema(name="long_term", description="bullish, bearish or neutral"),
    ResponseSchema(name="confidence", description="number between 0 and 1"),
    ResponseSchema(name="reasons", description="list of reasons"),
    ResponseSchema(name="risks", description="list of risks"),
    ResponseSchema(name="uncertainties", description="list of uncertainties"),
    ResponseSchema(name="assumptions", description="list of assumptions"),
    ResponseSchema(name="analysis", description="Entire Analysis Text")
]

parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = parser.get_format_instructions()