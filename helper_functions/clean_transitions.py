def clean_transition_column(tran_col):
    """
    When fed through excel, transition columns get turned into strings. 
    This turns them back to tuples.
    """
    return [tuple(y) for y in list(map( lambda x: x.strip("()").replace("'", "").split(", "), tran_col))]