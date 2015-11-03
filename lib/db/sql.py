# -*- coding: utf-8 -*-
create_table_edition = \
    """
    CREATE TABLE edition (
        code VARCHAR(8) PRIMARY KEY NOT NULL,
        releaseDate date NOT NULL,
        name VARCHAR(255) UNIQUE NOT NULL,
        type ENUM (
            'core', 'expansion', 'duel deck', 'commander', 'promo', 'box', 'un', 'reprint', 'from the vault',
            'planechase', 'masters', 'starter', 'premium deck', 'conspiracy', 'vanguard', 'archenemy'
        ) NOT NULL,
        block VARCHAR(50)
    )
    """


create_table_metacard = \
    """
    CREATE TABLE metacard (
        name VARCHAR(150) PRIMARY KEY,
        types SET (
            'Land', 'Creature', 'Sorcery', 'Instant', 'Artifact', 'Planeswalker', 'Enchantment', 'Tribal', 'Scheme',
            'Eaturecray', 'Enchant', 'Vanguard', 'Plane', 'Scariest', "You\'ll", 'Ever', 'See', 'Conspiracy',
            'Phenomenon', 'Player', 'token'
        ) NOT NULL,
        subtypes VARCHAR(80),
        supertypes SET('Legendary', 'Snow', 'World', 'Basic', 'Ongoing'),
        manaCost VARCHAR(50),
        power VARCHAR(8),
        toughness VARCHAR(8),
        colors SET('Red', 'Green', 'White', 'Blue', 'Black'),
        cmc FLOAT NOT NULL,
        orig_text TEXT
    )
    """

create_table_cards = \
    """
    CREATE TABLE card (
        card_id INT PRIMARY KEY AUTO_INCREMENT,
        multiverseid INT,
        name VARCHAR(150) NOT NULL,
        edition VARCHAR(8) NOT NULL,
        rarity SET ('Basic Land', 'Common', 'Uncommon', 'Rare', 'Mythic Rare', 'Special') NOT NULL,
        number VARCHAR(4) NOT NULL,
        version TINYINT NOT NULL,
        artist VARCHAR(150) NOT NULL,
        flavor TEXT,
        price FLOAT,

        FOREIGN KEY (name) REFERENCES metacard(name),
        FOREIGN KEY (edition) REFERENCES edition(code),
        UNIQUE (multiverseid, number)
    )
    """

create_table_tournament = \
    """
    CREATE TABLE tournament (
        name VARCHAR(150) PRIMARY KEY
    )
    """

create_table_card_legal_in_tournament = \
    """
    CREATE TABLE card_legal_in_tournament (
        card_name VARCHAR(150) NOT NULL,
        tournament_name VARCHAR(150) NOT NULL,
        type SET('Restricted', 'Legal') NOT NULL,

        FOREIGN KEY (card_name) REFERENCES metacard(name),
        FOREIGN KEY (tournament_name) REFERENCES tournament(name),
        UNIQUE (card_name, tournament_name)
    )
    """

create_table_user = \
    """
    CREATE TABLE user (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT FALSE
    )
    """

create_table_card_in_collection = \
    """
    CREATE TABLE card_in_collection (
        user_id INT NOT NULL,
        card_id INT NOT NULL,
        num_normal INT NOT NULL DEFAULT 0,
        num_foil INT NOT NULL DEFAULT 0,

        FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
        FOREIGN KEY (card_id) REFERENCES card(card_id),
        UNIQUE(user_id, card_id)
    )
    """

create_table_deck = \
    """
    CREATE TABLE deck (
        deck_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        deck_name VARCHAR(255) NOT NULL,

        FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
    )
    """

create_table_card_in_deck = \
    """
    CREATE TABLE card_in_deck(
        deck_id INT NOT NULL,
        card_name VARCHAR(150) NOT NULL,
        number SMALLINT NOT NULL DEFAULT 1,

        FOREIGN KEY (deck_id) REFERENCES deck(deck_id) ON DELETE CASCADE,
        FOREIGN KEY (card_name) REFERENCES metacard(name),
        UNIQUE(deck_id, card_name)
    )
    """

add_edition = \
    """
    INSERT INTO edition (code, releaseDate, name, type, block)
    VALUES (%(code)s, %(releaseDate)s, %(name)s, %(type)s, %(block)s)
    """


add_metacard = \
    """
    INSERT INTO metacard (name, types, subtypes, supertypes, manaCost, power, toughness, colors, cmc, orig_text)
    VALUES (
        %(name)s, %(types)s, %(subtypes)s, %(supertypes)s, %(manaCost)s, %(power)s, %(toughness)s, %(colors)s, %(cmc)s,
        %(text)s
    )
    """

add_card = \
    """
    INSERT INTO card (multiverseid, name, number, version, rarity, edition, artist, flavor)
    VALUES (%(multiverseid)s, %(name)s, %(number)s, %(version)s, %(rarity)s, %(edition)s, %(artist)s, %(flavor)s)
    """

add_tournament = \
    """
    INSERT INTO tournament (name)
    VALUES (%(name)s)
    """

allow_card_in_tournament = \
    """
    INSERT INTO card_legal_in_tournament (card_name, tournament_name, type)
    VALUES (%(card_name)s, %(tournament_name)s, %(type)s)
    """

metacard_constraints = [
    """
    CREATE TRIGGER `power_not_null_on_creature` BEFORE INSERT ON `metacard`
    FOR EACH ROW
    BEGIN
        IF (
            (FIND_IN_SET('Creature', NEW.types) = 1 AND FIND_IN_SET('enchant', NEW.types) = 0)
            AND (NEW.power IS NULL or NEW.toughness IS NULL)
            AND FIND_IN_SET('The', NEW.subtypes) = 0)
        THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error : the power of a creature cannot be NULL';
        END IF;
    END
    """,
]
