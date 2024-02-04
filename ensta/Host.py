import os
import json
from .SessionHost import SessionHost
from .lib.Exceptions import SessionError
from .Authentication import new_session_id


# noinspection PyMissingConstructor
class Host(SessionHost):

    DEFAULT_FILE: str = "ensta-web-session.txt"

    identifier: str = None
    password: str = None

    save: any = None
    load: any = None
    file: str | None = None

    proxy: dict[str, str] = None
    totp_token: str = None

    def __init__(
        self,
        identifier: str,
        password: str,
        file: str = None,
        save: any = None,
        load: any = None,
        proxy: dict[str, str] = None,
        totp_token: str = None
    ) -> None:

        """
        Login using your username/email and password.
        :param identifier: Your Instagram Username or Email
        :param password: Your Instagram Password
        :param file: (Optional) Name of file to store session_data in. Eg: "session.txt"
        :param save: (Optional) Name of a function which will be called to save the generated session_data
        :param load: (Optional) Name of a function which will be called to receive the session_data
        :param proxy: (Optional) JSON Object of proxy to be used. See https://github.com/diezo/ensta
        :param totp_token: (Optional) Your TOTP Key generated by Instagram while setting up 2FA (If 2FA is turned on)
        """

        self.identifier: str = identifier
        self.password: str = password
        self.file: str = file
        self.save: any = save
        self.load: any = load
        self.proxy: dict[str, str] = proxy
        self.totp_token = totp_token

        if self.file is None and self.load is None: self.file: str = self.DEFAULT_FILE
        self.load_session()

    def load_session(self, sid: str = None) -> any:
        if self.file is None and self.load is None and sid is None:
            raise Exception("Neither Load Function nor File Name was passed to load SessionId.")

        if sid:
            try: super().__init__(sid, self.proxy)
            except SessionError: return self.new_session()

        elif self.load:
            session_data: str = self.load().strip()

            if session_data == "": return self.new_session()
            else:
                try: super().__init__(session_data, self.proxy)
                except SessionError: return self.new_session()

        elif self.file:
            if not os.path.exists(self.file): return self.new_session()

            with open(self.file, "r") as reading:
                if (session_data := reading.read().strip()) == "": return self.new_session()

                else:
                    # noinspection PyBroadException
                    try:
                        if json.loads(session_data)["identifier"] != self.identifier: raise Exception()
                        super().__init__(session_data, self.proxy)
                    except Exception: return self.new_session()

    def new_session(self) -> None:
        session_data: str = new_session_id(
            user_identifier=self.identifier,
            password=self.password,
            proxy=self.proxy,
            totp_token=self.totp_token
        )
        
        if self.save: self.save(session_data)

        if self.file:
            with open(self.file, "w") as writing: writing.write(session_data)

        self.load_session(session_data)
