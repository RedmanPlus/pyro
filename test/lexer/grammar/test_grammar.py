from src.lexer.grammar_loader import GrammarLoader


class TestGrammarLoader:
    def test_parse_grammar_file(self, bnf_example: str) -> None:
        loader = GrammarLoader(bnf_example)
        token_defs = loader()

        assert len(token_defs) == 1
        assert token_defs[0].type_name == "foo"
