#!/usr/bin/env python3
"""
This module defines the DB class for interacting
with the database using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound, InvalidRequestError
from sqlalchemy.orm.session import Session
from user import User, Base


class DB:
    """
    DB class for database interactions.
    """

    def __init__(self) -> None:
        """
        Initialize a new DB instance.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Memoized session object.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Add a new user to the database.

        :param email: User's email
        :param hashed_password: Hashed password
        :return: User object
        :raises Exception: If an error occurs while adding the user.
        """
        try:
            new_user = User(email=email, hashed_password=hashed_password)
            self._session.add(new_user)
            self._session.commit()
            return new_user
        except Exception as e:
            self._session.rollback()
            raise e

    def find_user_by(self, **kwargs) -> User:
        """
        Find a user by specified attributes.

        :param kwargs: Keyword arguments to filter users
        :return: User object
        :raises NoResultFound: When no user is found
        :raises InvalidRequestError: When invalid query arguments are passed
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if user is None:
                raise NoResultFound("No user found.")
            return user
        except InvalidRequestError:
            raise InvalidRequestError("Invalid query arguments.")

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user's attributes.

        :param user_id: User's ID
        :param kwargs: Updated user attributes
        :raises NoResultFound: When no user is found
        :raises InvalidRequestError: When invalid query arguments are passed
        :raises ValueError: When invalid attribute is passed
        """
        try:
            user = self.find_user_by(id=user_id)
            for attr, value in kwargs.items():
                if hasattr(user, attr):
                    setattr(user, attr, value)
                else:
                    raise ValueError(f"Invalid attribute: {attr}")
            self._session.commit()
        except NoResultFound:
            raise NoResultFound("No user found.")
        except InvalidRequestError:
            raise InvalidRequestError("Invalid query arguments.")
