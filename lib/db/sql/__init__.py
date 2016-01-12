create_table_card_legal_in_tournament = \
    """
    CREATE TABLE card_legal_in_tournament (
        card_name VARCHAR(150) NOT NULL,
        tournament_name VARCHAR(150) NOT NULL,
        type SET('Restricted', 'Legal') NOT NULL,

        FOREIGN KEY (card_name) REFERENCES metacard(name) ON DELETE RESTRICT ON UPDATE RESTRICT,
        FOREIGN KEY (tournament_name) REFERENCES tournament(name) ON DELETE RESTRICT ON UPDATE RESTRICT ,
        UNIQUE (card_name, tournament_name)
    )
    """


allow_card_in_tournament = \
    """
    INSERT INTO card_legal_in_tournament (card_name, tournament_name, type)
    VALUES (%(card_name)s, %(tournament_name)s, %(type)s)
    """
