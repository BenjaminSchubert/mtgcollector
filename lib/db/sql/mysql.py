class MySQL:
    # user functions
    create_user = """ INSERT INTO user (username, email, password) VALUES (%(username)s, %(email)s, %(password)s) """
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
