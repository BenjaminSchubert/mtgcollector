class MySQL:
    # user
    insert_user = """ INSERT INTO user (username, email, password) VALUES (%(username)s, %(email)s, %(password)s) """
    set_admin = """ UPDATE user SET is_admin = %(admin)s WHERE user_id = %(user_id)s"""
    get_users = """ SELECT * FROM user ORDER BY username """
    get_users_with_limit = """ SELECT * FROM user ORDER BY username LIMIT %(limit)s """
    get_user_by_id = """ SELECT * FROM user WHERE user_id = %(user_id)s """
    select_user = """ SELECT * FROM user WHERE username = %(identifier)s or email = %(identifier)s """

    create_table_user = \
        """
        CREATE TABLE user (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT FALSE
        )
        """

    user_constraints = [
        """
        CREATE TRIGGER `user_cant_have_username_same_as_other_email` BEFORE INSERT ON `user`
        FOR EACH ROW
        BEGIN
            IF(
                EXISTS(SELECT user_id FROM user WHERE email = NEW.username)
            OR
                EXISTS(SELECT user_id FROM user WHERE username = NEW.email)
            )
            THEN
                SIGNAL SQLSTATE '23000' SET MESSAGE_TEXT = \
                "A user cannot have a username the same as another user's email";
            END IF;
        END
        """
    ]

    # metacard
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
        """
    ]

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
            power VARCHAR(4),
            toughness VARCHAR(4),
            colors SET('Red', 'Green', 'White', 'Blue', 'Black'),
            cmc FLOAT NOT NULL,
            orig_text TEXT
        )
        """

    insert_metacard = \
        """
        INSERT INTO metacard (name, types, subtypes, supertypes, manaCost, power, toughness, colors, cmc, orig_text)
        VALUES (
            %(name)s, %(types)s, %(subtypes)s, %(supertypes)s, %(manaCost)s, %(power)s, %(toughness)s, %(colors)s,
             %(cmc)s, %(text)s
        )
        ON DUPLICATE KEY UPDATE
            name=VALUES(name), types=VALUES(types), subtypes=VALUES(subtypes), supertypes=VALUES(supertypes),
            manaCost=VALUES(manaCost), power=VALUES(power), toughness=VALUES(toughness), colors=VALUES(colors),
            cmc=VALUES(cmc), orig_text=VALUES(orig_text)
        """

    get_metacards_ids = \
        """
        SELECT card.card_id
        FROM metacard
        INNER JOIN card ON card.name = metacard.name
        WHERE {selection}
        GROUP BY metacard.name
        ORDER BY {order}
        """

    # card
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
            price DECIMAL(7,2),

            FOREIGN KEY (name) REFERENCES metacard(name),
            FOREIGN KEY (edition) REFERENCES edition(code),
            UNIQUE (multiverseid, edition, number, version)
        )
        """

    insert_card = \
        """
        INSERT INTO card (multiverseid, name, number, version, rarity, edition, artist, flavor)
        VALUES (%(multiverseid)s, %(name)s, %(number)s, %(version)s, %(rarity)s, %(edition)s, %(artist)s, %(flavor)s)
        ON DUPLICATE KEY UPDATE
            name=VALUES(name), number=VALUES(number), version=VALUES(version), rarity=VALUES(version),
            edition=VALUES(edition), artist=VALUES(artist), flavor=VALUES(flavor)
        """

    # edition
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

    insert_edition = \
        """
        INSERT INTO edition (code, releaseDate, name, type, block)
        VALUES (%(code)s, %(releaseDate)s, %(name)s, %(type)s, %(block)s)
        ON DUPLICATE KEY UPDATE
            releaseDate=VALUES(releaseDate), name=VALUES(name), type=VALUES(type), block=VALUES(block)
        """

    get_editions_name_id = \
        """
        SELECT code, name FROM edition ORDER BY name
        """

    # tournament
    create_table_tournament = \
        """
        CREATE TABLE tournament (
            name VARCHAR(150) PRIMARY KEY
        )
        """

    insert_tournament = \
        """
        INSERT INTO tournament (name)
        VALUES (%(name)s)
        ON DUPLICATE KEY UPDATE name=VALUES(name)
        """
