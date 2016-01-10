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


create_table_deck = \
    """
    CREATE TABLE deck (
        deck_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        deck_name VARCHAR(255) NOT NULL,

        FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """

create_table_card_in_deck = \
    """
    CREATE TABLE card_in_deck(
        deck_id INT NOT NULL,
        card_name VARCHAR(150) NOT NULL,
        number SMALLINT NOT NULL DEFAULT 1,

        FOREIGN KEY (deck_id) REFERENCES deck(deck_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (card_name) REFERENCES metacard(name) ON DELETE RESTRICT ON UPDATE CASCADE,
        UNIQUE(deck_id, card_name)
    )
    """






allow_card_in_tournament = \
    """
    INSERT INTO card_legal_in_tournament (card_name, tournament_name, type)
    VALUES (%(card_name)s, %(tournament_name)s, %(type)s)
    """
