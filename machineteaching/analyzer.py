import io
import tokenize
from sklearn.feature_extraction.text import CountVectorizer

vectorizer_params = {
    "ngram_range": (1,3)
}

removed_itens = ['NEWLINE', 'ENDMARKER', "NL", 'COMMENT', 'ERRORTOKEN']
allowed_itens = ['NAME', 'OP', 'INDENT', 'DEDENT', 'STRING', 'NUMBER']

def python_analyzer(doc):
    words = []
    not_found = []
    vectorizer = CountVectorizer(**vectorizer_params)
    file = io.StringIO(doc)
    try:
        for token in tokenize.generate_tokens(file.readline):
            token_type = tokenize.tok_name[token[0]]

            # Redundant conditional to make sure we're getting all the token types
            if token_type not in removed_itens:
                if token_type in allowed_itens:
                    # If it's a variable or reserved name, keep it
                    if token_type == "NAME":
                        words.append(token[1])
                    elif token_type == "INDENT":
                        # Adding indent for all indentations
                        words.append("is_indent")
                    elif token_type == "DEDENT":
                        # Adding dedent for all indentations
                        words.append("is_dedent")
                    elif token_type == "STRING":
                        # Adding is_string for every string
                        words.append("is_string")
                    elif token_type == "NUMBER":
                        # Adding is_number for every number:
                        words.append("is_number")
                    elif token_type == "OP":
                        # If it's operator, then we'll divide in several types
                        lookup = {
                            "+": "is_op_arit",
                            "+=": "is_op_arit",
                            "-": "is_op_arit",
                            "*": "is_op_arit",
                            "**": "is_op_arit",
                            "/": "is_op_arit",
                            "//": "is_op_arit",
                            "%": "is_op_arit",
                            ">": "is_op_logic",
                            "<": "is_op_logic",
                            ">=": "is_op_logic",
                            "<=": "is_op_logic",
                            "==": "is_op_logic",
                            "-=": "is_op_logic",
                            "!=": "is_op_logic",
                            "[": "is_list",
    #                         "]": "is_list",
                            "{": "is_dict",
    #                         "}": "is_dict",
                            ".": "is_class",
                            "=": "is_attribution",
                            ":": "is_block"
                        }
                        try:
                            words.append(lookup[token[1]])
                        except KeyError:
                            not_found.append(token[1])
    #     print("not found: %s" % set(not_found))
    except (IndentationError, tokenize.TokenError):
        pass
    return vectorizer._word_ngrams(words)
