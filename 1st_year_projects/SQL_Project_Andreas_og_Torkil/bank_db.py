import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import oracledb


BIRTHDAY_COLUMN = "F\u00d8\u00d0INGARDAG"
NEW_PERSON_BIRTH_ARGUMENT = "P_F\u00d8\u00d0INGARDAG"
PROC_NEW_PERSON = "new_per"
PROC_NEW_STAFF = "new_starv"
PROC_UPDATE_STAFF = "rolle_broytari"
PROC_ADD_CHILD = "barn"
PROC_MARRY = "n\u00fdggj_hj\u00fan"
PROC_DIVORCE = "end_hj\u00fan"
PROC_NEW_DRAFT = "nyggj_kladda"
PROC_BOOK_DRAFT = "boka_kladdu"
PROC_REJECT_DRAFT = "avvisa_kladdu"
ORACLE_CALL_TIMEOUT_MS = 15000


class BankClientError(RuntimeError):
    pass


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[tuple[Any, ...]]


class OracleBankClient:
    DATASETS = {
        "Postcodes": (
            "select postkota, bygd from postkota order by postkota"
        ),
        "Addresses": (
            "select bústað_id as bustad_id, postkota, gøta as gota, húsnummar as husnummar, "
            "hædd as haedd, rúmnummar as rumnummar from bústað order by bústað_id"
        ),
        "Account types": (
            "select kontoslag_id, slag_navn, credit_renta, debit_renta "
            "from kontoslag order by kontoslag_id"
        ),
        "Persons": (
            "select p_id, p_tal, fornavn, eftirnavn, "
            "f\u00f8\u00f0ingardag as birth_date, kyn, b\u00fasta\u00f0_id as bustad_id "
            "from pers order by p_id"
        ),
        "Customers": (
            "select kunda_id, p_id, stovningar_dato, slett_dato "
            "from kundi order by kunda_id"
        ),
        "Accounts": (
            "select konto_id, saldo, kontotypa, eigari_p_id as eigari_kunda_id "
            "from konto order by konto_id"
        ),
        "Staff": (
            "select p_id as staff_person_id, starv_navn, lon, atgongd_typa "
            "from starvsfolk order by p_id"
        ),
        "Marriages": (
            "select hj\u00fanaband_id as hjunaband_id, p1_id, p2_id, gift_dato, skild_dato "
            "from hj\u00fanaband order by hj\u00fanaband_id"
        ),
        "Children": (
            "select id, p1_id, p2_id, barn_id from b\u00f8rn order by id"
        ),
        "Drafts": (
            "select kladdu_id, flyting, fr\u00e1_id as fra_id, til_id, "
            "slag, status, bokad_dato, dato "
            "from kladda order by kladdu_id desc"
        ),
        "Customer totals": (
            "select kunda_id, p_id, tal_av_kontum, samla\u00f0_saldo as samlad_saldo "
            "from v_kundi_samla_saldo order by kunda_id"
        ),
        "Account statement": (
            "select log_id, konto_id, eigari_p_id, eigari_navn, log_dato, saldo_broyting, "
            "leypandi_saldo, mottakari_konto_id, mottakari_p_id, mottakari_navn, tekst, "
            "nuverandi_saldo from v_kontoavrit order by log_id desc"
        ),
        "Parent-child accounts": (
            "select foreldur_id, barn_id, konto_id, saldo "
            "from v_foreldur_barn_kontur order by foreldur_id, barn_id, konto_id"
        ),
        "Spouse accounts": (
            "select brukari_p_id, maki_p_id, konto_id, saldo "
            "from v_hjunafelaga_kontur order by brukari_p_id, maki_p_id, konto_id"
        ),
    }

    def __init__(self) -> None:
        self.connection: oracledb.Connection | None = None
        self.birth_mode = "varchar"
        self.booking_actor_column = "BOKAD_AV_P_ID"

    @property
    def is_connected(self) -> bool:
        return self.connection is not None

    def connect(self, user: str, password: str, dsn: str) -> str:
        self.close()
        try:
            self.connection = oracledb.connect(user=user, password=password, dsn=dsn)
            self.connection.call_timeout = ORACLE_CALL_TIMEOUT_MS
            self.birth_mode = self._detect_birth_mode()
            self.booking_actor_column = self._detect_booking_actor_column()
            return self.birth_mode
        except oracledb.DatabaseError as exc:
            self.connection = None
            raise BankClientError(self._format_db_error(exc)) from exc

    def close(self) -> None:
        if self.connection is not None:
            try:
                self.connection.close()
            finally:
                self.connection = None

    def fetch_dataset(self, name: str) -> QueryResult:
        if name == "Drafts":
            return self.fetch_query(self._drafts_query())
        return self.fetch_query(self.DATASETS[name])

    def fetch_query(self, sql: str, params: list[Any] | tuple[Any, ...] | None = None) -> QueryResult:
        conn = self._require_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or [])
                columns = [item[0] for item in cursor.description or []]
                rows = cursor.fetchall()
                return QueryResult(columns=columns, rows=rows)
        except oracledb.DatabaseError as exc:
            raise BankClientError(self._format_db_error(exc)) from exc

    def fetch_login_profile(self, p_tal: str) -> dict[str, Any]:
        normalized_p_tal = self._normalize_p_tal(p_tal)
        result = self.fetch_query(
            """
            select p.p_id,
                   p.p_tal,
                   p.fornavn,
                   p.eftirnavn,
                   case
                       when exists (
                           select 1
                           from kundi ku
                           where ku.p_id = p.p_id
                       ) then 1
                       else 0
                   end as is_customer,
                   (
                       select count(*)
                       from konto k
                       join kundi ku
                         on ku.kunda_id = k.eigari_p_id
                       where ku.p_id = p.p_id
                   ) as account_count,
                   s.atgongd_typa
            from pers p
            left join starvsfolk s
              on s.p_id = p.p_id
            where p.p_tal = :1
            """,
            [normalized_p_tal],
        )

        if not result.rows:
            raise BankClientError(f"No person found with p-tal {normalized_p_tal}.")

        person_id, stored_p_tal, first_name, last_name, is_customer, account_count, access_type = result.rows[0]
        normalized_access = str(access_type).upper() if access_type else "PERSON"
        if normalized_access not in {"ADMIN", "STARVSFOLK"}:
            normalized_access = "PERSON"

        return {
            "person_id": int(person_id),
            "p_tal": str(stored_p_tal),
            "first_name": str(first_name or ""),
            "last_name": str(last_name or ""),
            "full_name": " ".join(part for part in [str(first_name or "").strip(), str(last_name or "").strip()] if part),
            "is_customer": bool(is_customer),
            "account_count": int(account_count or 0),
            "access_type": normalized_access,
            "is_staff": normalized_access in {"STARVSFOLK", "ADMIN"},
            "is_admin": normalized_access == "ADMIN",
        }

    def fetch_person_dashboard(self, p_tal: str) -> dict[str, Any]:
        normalized_p_tal = self._normalize_p_tal(p_tal)
        person = self.fetch_query(
            """
            select p_id, p_tal, fornavn, eftirnavn,
                   føðingardag as birth_date, kyn, bústað_id as bustad_id
            from pers
            where p_tal = :1
            """,
            [normalized_p_tal],
        )

        if not person.rows:
            raise BankClientError(f"No person found with p-tal {normalized_p_tal}.")

        person_id = int(person.rows[0][0])
        sections = [
            (
                "Person",
                person,
            ),
            (
                "Staff",
                self.fetch_query(
                    f"""
                    select p_id as staff_person_id, starv_navn, lon, atgongd_typa
                    from starvsfolk
                    where p_id = :1
                    order by p_id
                    """,
                    [person_id],
                ),
            ),
            (
                "Customer totals",
                self.fetch_query(
                    f"""
                    select kunda_id, p_id, tal_av_kontum, samlað_saldo as samlad_saldo
                    from v_kundi_samla_saldo
                    where p_id = :1
                    order by kunda_id
                    """,
                    [person_id],
                ),
            ),
            (
                "Owned accounts",
                self.fetch_query(
                    f"""
                    select k.konto_id, k.saldo, k.kontotypa, k.eigari_p_id as eigari_kunda_id
                    from konto k
                    join kundi ku
                      on ku.kunda_id = k.eigari_p_id
                    where ku.p_id = :1
                    order by k.konto_id
                    """,
                    [person_id],
                ),
            ),
            (
                "Account statement",
                self.fetch_query(
                    """
                    select log_id, konto_id, eigari_p_id, eigari_navn, log_dato, saldo_broyting,
                           leypandi_saldo, mottakari_konto_id, mottakari_p_id, mottakari_navn,
                           tekst, nuverandi_saldo
                    from v_kontoavrit
                    where eigari_p_id = :1
                    order by log_id desc
                    """,
                    [person_id],
                ),
            ),
            (
                "Spouse accounts",
                self.fetch_query(
                    """
                    select brukari_p_id, maki_p_id, konto_id, saldo
                    from v_hjunafelaga_kontur
                    where brukari_p_id = :1
                    order by maki_p_id, konto_id
                    """,
                    [person_id],
                ),
            ),
            (
                "Parent-child accounts",
                self.fetch_query(
                    """
                    select foreldur_id, barn_id, konto_id, saldo
                    from v_foreldur_barn_kontur
                    where foreldur_id = :1 or barn_id = :1
                    order by foreldur_id, barn_id, konto_id
                    """,
                    [person_id, person_id],
                ),
            ),
            (
                "Related drafts",
                self.fetch_query(
                    f"""
                    select kladdu_id, flyting, frá_id as fra_id, til_id,
                           slag, status, {self.booking_actor_column} as bokad_av_staff_person_id, bokad_dato, dato
                    from kladda
                    where frá_id in (
                        select k.konto_id
                        from konto k
                        join kundi ku
                          on ku.kunda_id = k.eigari_p_id
                        where ku.p_id = :1
                    )
                       or til_id in (
                        select k.konto_id
                        from konto k
                        join kundi ku
                          on ku.kunda_id = k.eigari_p_id
                        where ku.p_id = :1
                    )
                    order by kladdu_id desc
                    """,
                    [person_id, person_id],
                ),
            ),
        ]

        return {
            "p_tal": normalized_p_tal,
            "person_id": person_id,
            "sections": [{"title": title, "result": result} for title, result in sections],
        }

    def create_person(
        self,
        fornavn: str,
        eftirnavn: str,
        birth_value: str,
        kyn: str,
        bustad_id: int,
    ) -> None:
        normalized_birth = self._normalize_birth_value(birth_value)
        if self.birth_mode == "date":
            self._execute_block(
                "BEGIN new_per(:1, :2, TO_DATE(:3, 'DDMMYYYY'), :4, :5); END;",
                [fornavn, eftirnavn, normalized_birth, kyn, bustad_id],
            )
        else:
            self._execute_named_procedure(
                PROC_NEW_PERSON,
                [fornavn, eftirnavn, normalized_birth, kyn, bustad_id],
            )

    def seed_defaults(self) -> None:
        self._execute_block(
            """
            BEGIN
                BEGIN
                    INSERT INTO postkota (postkota, bygd)
                    VALUES (100, 'Torshavn');
                EXCEPTION
                    WHEN DUP_VAL_ON_INDEX THEN NULL;
                END;

                BEGIN
                    INSERT INTO bústað (bústað_id, postkota, gøta, húsnummar, hædd, rúmnummar)
                    VALUES (1, 100, 'Heimavegur', 1, 1, 1);
                EXCEPTION
                    WHEN DUP_VAL_ON_INDEX THEN NULL;
                END;

                BEGIN
                    INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
                    VALUES ('000', 'konto_hja_bankanum', 0, 0);
                EXCEPTION
                    WHEN DUP_VAL_ON_INDEX THEN NULL;
                END;

                BEGIN
                    INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
                    VALUES ('100', 'lan', 0.05, 0);
                EXCEPTION
                    WHEN DUP_VAL_ON_INDEX THEN NULL;
                END;

                BEGIN
                    INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
                    VALUES ('200', 'nytsla', 0.1, 0.005);
                EXCEPTION
                    WHEN DUP_VAL_ON_INDEX THEN NULL;
                END;

                BEGIN
                    INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
                    VALUES ('300', 'uppsparing', 0.1, 0.01);
                EXCEPTION
                    WHEN DUP_VAL_ON_INDEX THEN NULL;
                END;

                BEGIN
                    INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
                    VALUES ('400', 'odefinera', 0.1, 0);
                EXCEPTION
                    WHEN DUP_VAL_ON_INDEX THEN NULL;
                END;
            END;
            """,
            [],
        )
        return
        blocks = [
            "BEGIN INSERT INTO postkota (postkota, bygd) VALUES (100, 'Tórshavn'); "
            "EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL; END;",
            "BEGIN INSERT INTO bústað (bústað_id, postkota, gøta, húsnummar, hædd, rúmnummar) "
            "VALUES (1, 100, 'Heimavegur', 1, 1, 1); "
            "EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL; END;",
            "BEGIN INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta) "
            "VALUES ('000', 'konto_hja_bankanum', 0, 0); "
            "EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL; END;",
            "BEGIN INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta) "
            "VALUES ('100', 'lán', 0.05, 0); "
            "EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL; END;",
            "BEGIN INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta) "
            "VALUES ('200', 'nýtsla', 0.1, 0.005); "
            "EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL; END;",
            "BEGIN INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta) "
            "VALUES ('300', 'uppsparing', 0.1, 0.01); "
            "EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL; END;",
            "BEGIN INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta) "
            "VALUES ('400', 'ódefinera', 0.1, 0); "
            "EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL; END;",
        ]
        for block in blocks:
            self._execute_block(block, [])

    def create_customer(self, person_id: int, password: str) -> None:
        self._execute_statement(
            "INSERT INTO kundi (loynuorð, p_id) VALUES (:1, :2)",
            [password, person_id],
        )

    def create_account(self, customer_id: int, account_type: str) -> None:
        self._execute_statement(
            "INSERT INTO konto (saldo, kontotypa, eigari_p_id) VALUES (0, :1, :2)",
            [account_type, customer_id],
        )

    def bootstrap_admin(self, person_id: int, title: str, salary: Decimal) -> None:
        self._execute_statement(
            "INSERT INTO starvsfolk (starv_navn, lon, p_id, atgongd_typa) VALUES (:1, :2, :3, 'ADMIN')",
            [title, salary, person_id],
        )

    def create_staff(self, admin_person_id: int, person_id: int, title: str, salary: Decimal) -> None:
        self._execute_named_procedure(
            PROC_NEW_STAFF,
            [admin_person_id, person_id, title, salary],
        )

    def update_staff(
        self,
        admin_staff_id: int,
        staff_id: int,
        title: str | None,
        salary: Decimal | None,
        access_type: str | None,
    ) -> None:
        self._execute_named_procedure(
            PROC_UPDATE_STAFF,
            [admin_staff_id, staff_id, title, salary, access_type],
        )

    def marry(self, person_one_id: int, person_two_id: int) -> None:
        self._execute_named_procedure(PROC_MARRY, [person_one_id, person_two_id])

    def divorce(self, person_one_id: int, person_two_id: int) -> None:
        self._execute_named_procedure(PROC_DIVORCE, [person_one_id, person_two_id])

    def add_child(self, parent_one_id: int, parent_two_id: int | None, child_id: int) -> None:
        self._execute_named_procedure(PROC_ADD_CHILD, [parent_one_id, parent_two_id, child_id])

    def create_draft(
        self,
        user_person_id: int,
        amount: Decimal,
        from_account: str | None,
        to_account: str | None,
        own_text: str | None,
        recipient_text: str | None,
        draft_type: str,
    ) -> None:
        self._execute_named_procedure(
            PROC_NEW_DRAFT,
            [user_person_id, amount, from_account, to_account, own_text, recipient_text, draft_type],
        )

    def book_draft(self, staff_id: int, draft_id: int) -> None:
        self._execute_named_procedure(PROC_BOOK_DRAFT, [staff_id, draft_id])

    def reject_draft(self, staff_id: int, draft_id: int) -> None:
        self._execute_named_procedure(PROC_REJECT_DRAFT, [staff_id, draft_id])

    def _detect_birth_mode(self) -> str:
        conn = self._require_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    select data_type
                    from user_arguments
                    where object_name = 'NEW_PER'
                      and argument_name = :argument_name
                    """,
                    [NEW_PERSON_BIRTH_ARGUMENT],
                )
                row = cursor.fetchone()
                if row and row[0]:
                    return "date" if row[0].upper() == "DATE" else "varchar"

                cursor.execute(
                    """
                    select data_type
                    from user_tab_columns
                    where table_name = 'PERS'
                      and column_name = :column_name
                    """,
                    [BIRTHDAY_COLUMN],
                )
                row = cursor.fetchone()
                if row and row[0] and row[0].upper() == "DATE":
                    return "date"
        except oracledb.DatabaseError:
            pass
        return "varchar"

    def _detect_booking_actor_column(self) -> str:
        conn = self._require_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    select column_name
                    from user_tab_columns
                    where table_name = 'KLADDA'
                      and column_name in ('BOKAD_AV_P_ID', 'BOKAD_AV_STARV_ID')
                    order by case column_name
                        when 'BOKAD_AV_P_ID' then 1
                        else 2
                    end
                    """
                )
                row = cursor.fetchone()
                if row and row[0]:
                    return str(row[0])
        except oracledb.DatabaseError:
            pass
        return "BOKAD_AV_P_ID"

    def _drafts_query(self) -> str:
        return (
            "select kladdu_id, flyting, fr\u00e1_id as fra_id, til_id, "
            f"slag, status, {self.booking_actor_column} as bokad_av_staff_person_id, bokad_dato, dato "
            "from kladda order by kladdu_id desc"
        )

    def _execute_named_procedure(self, procedure_name: str, params: list[Any]) -> None:
        placeholders = ", ".join(f":{index}" for index in range(1, len(params) + 1))
        self._execute_block(f"BEGIN {procedure_name}({placeholders}); END;", params)

    def _execute_block(self, block: str, params: list[Any]) -> None:
        conn = self._require_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(block, params)
            conn.commit()
        except oracledb.DatabaseError as exc:
            conn.rollback()
            raise BankClientError(self._format_db_error(exc)) from exc

    def _execute_statement(self, sql: str, params: list[Any]) -> None:
        conn = self._require_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
            conn.commit()
        except oracledb.DatabaseError as exc:
            conn.rollback()
            raise BankClientError(self._format_db_error(exc)) from exc

    def _require_connection(self) -> oracledb.Connection:
        if self.connection is None:
            raise BankClientError("Connect to the Oracle database first.")
        try:
            self.connection.ping()
        except oracledb.DatabaseError as exc:
            self.close()
            raise BankClientError(
                "Oracle connection was lost. Click Reconnect and try again."
            ) from exc
        return self.connection

    @staticmethod
    def _format_db_error(exc: oracledb.DatabaseError) -> str:
        error = exc.args[0] if exc.args else exc
        return getattr(error, "message", str(exc)).strip()

    @staticmethod
    def _normalize_birth_value(raw_value: str) -> str:
        cleaned = raw_value.strip()
        if not cleaned:
            raise BankClientError("Birth date is required.")

        for fmt in ("%d%m%Y", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(cleaned, fmt).strftime("%d%m%Y")
            except ValueError:
                continue

        digits_only = "".join(ch for ch in cleaned if ch.isdigit())
        if len(digits_only) == 8:
            try:
                return dt.datetime.strptime(digits_only, "%d%m%Y").strftime("%d%m%Y")
            except ValueError as exc:
                raise BankClientError("Birth date must be a valid DDMMYYYY value.") from exc

        raise BankClientError("Birth date must be DDMMYYYY or YYYY-MM-DD.")

    @staticmethod
    def _normalize_p_tal(raw_value: str) -> str:
        cleaned = raw_value.strip()
        if not cleaned:
            raise BankClientError("P-tal is required.")
        if not cleaned.isdigit():
            raise BankClientError("P-tal must contain digits only.")
        return cleaned
