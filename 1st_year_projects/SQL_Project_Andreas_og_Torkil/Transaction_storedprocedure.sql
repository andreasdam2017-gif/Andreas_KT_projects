CREATE OR REPLACE PROCEDURE nyggj_kladda (
    brukari_p_id   IN NUMBER,
    flyting        IN NUMBER,
    fra_id         IN VARCHAR2,
    til_id         IN VARCHAR2,
    egintekst      IN VARCHAR2,
    mottokutekst   IN VARCHAR2,
    slag           IN VARCHAR2
) IS
    dummy NUMBER;
BEGIN
    IF brukari_p_id IS NULL THEN
        RAISE_APPLICATION_ERROR(-20001, 'ERROR: Brúkari má veljast.');
    END IF;

    IF flyting IS NULL OR flyting <= 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'ERROR: Flyting má vera yvir 0.');
    END IF;

    IF slag IS NULL OR slag NOT IN ('INNSETING', 'UTTOKA', 'FLYTING') THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERROR: Ógildigt slag.');
    END IF;

    SELECT p_id
    INTO dummy
    FROM pers
    WHERE p_id = brukari_p_id;

    IF slag = 'INNSETING' THEN
        IF til_id IS NULL OR fra_id IS NOT NULL THEN
            RAISE_APPLICATION_ERROR(-20004, 'ERROR: INNSETING krevur bert til-konto.');
        END IF;

        SELECT 1
        INTO dummy
        FROM konto k
        JOIN kundi ku
            ON ku.kunda_id = k.eigari_p_id
        WHERE k.konto_id = til_id
          AND ku.p_id = brukari_p_id;

    ELSIF slag = 'UTTOKA' THEN
        IF fra_id IS NULL OR til_id IS NOT NULL THEN
            RAISE_APPLICATION_ERROR(-20005, 'ERROR: UTTOKA krevur bert frá-konto.');
        END IF;

        SELECT 1
        INTO dummy
        FROM konto k
        JOIN kundi ku
            ON ku.kunda_id = k.eigari_p_id
        WHERE k.konto_id = fra_id
          AND ku.p_id = brukari_p_id;

    ELSIF slag = 'FLYTING' THEN
        IF fra_id IS NULL OR til_id IS NULL THEN
            RAISE_APPLICATION_ERROR(-20006, 'ERROR: FLYTING krevur bæði frá- og til-konto.');
        END IF;

        IF fra_id = til_id THEN
            RAISE_APPLICATION_ERROR(-20007, 'ERROR: Frá- og til-konto kunnu ikki vera eins.');
        END IF;

        SELECT 1
        INTO dummy
        FROM konto k
        JOIN kundi ku
            ON ku.kunda_id = k.eigari_p_id
        WHERE k.konto_id = fra_id
          AND ku.p_id = brukari_p_id;

        SELECT 1
        INTO dummy
        FROM konto
        WHERE konto_id = til_id;
    END IF;

    INSERT INTO kladda (
        flyting,
        frá_id,
        til_id,
        egintekst,
        mottokutekst,
        slag,
        status,
        dato
    )
    VALUES (
        flyting,
        fra_id,
        til_id,
        egintekst,
        mottokutekst,
        slag,
        'OAVGJORD',
        SYSDATE
    );

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20008, 'ERROR: Persónur ella konto fannst ikki, ella kontoin er ikki tín.');
    WHEN OTHERS THEN
        RAISE;
END nyggj_kladda;
/

CREATE OR REPLACE PROCEDURE boka_kladdu (
    brukari_p_id IN NUMBER,
    kladdu_id        IN NUMBER
) IS
    atgongd        starvsfolk.atgongd_typa%TYPE;
    flyting        kladda.flyting%TYPE;
    fra_id         kladda.frá_id%TYPE;
    til_id         kladda.til_id%TYPE;
    egintekst      kladda.egintekst%TYPE;
    mottokutekst   kladda.mottokutekst%TYPE;
    slag           kladda.slag%TYPE;
    status         kladda.status%TYPE;
    fra_saldo      konto.saldo%TYPE;
    til_saldo      konto.saldo%TYPE;
BEGIN
    SELECT atgongd_typa
    INTO atgongd
    FROM starvsfolk
    WHERE p_id = brukari_p_id;

    IF atgongd != 'STARVSFOLK' AND atgongd != 'ADMIN' THEN
        RAISE_APPLICATION_ERROR(-20001, 'ERROR: Bert starvsfólk ella admin kunnu bóka.');
    END IF;

    SELECT flyting, frá_id, til_id, egintekst, mottokutekst, slag, status
    INTO flyting, fra_id, til_id, egintekst, mottokutekst, slag, status
    FROM kladda
    WHERE kladdu_id = kladdu_id
    FOR UPDATE;

    IF status != 'OAVGJORD' THEN
        RAISE_APPLICATION_ERROR(-20002, 'ERROR: Kladdan er longu viðgjørd.');
    END IF;

    IF slag = 'INNSETING' THEN
        SELECT saldo
        INTO til_saldo
        FROM konto
        WHERE konto_id = til_id
        FOR UPDATE;

        INSERT INTO loggur (
            konto_id,
            saldo_broyting,
            móttakari_id,
            tekst
        )
        VALUES (
            til_id,
            flyting,
            NULL,
            mottokutekst
        );

    ELSIF slag = 'UTTOKA' THEN
        SELECT saldo
        INTO fra_saldo
        FROM konto
        WHERE konto_id = fra_id
        FOR UPDATE;

        IF flyting > fra_saldo THEN
            RAISE_APPLICATION_ERROR(-20003, 'ERROR: Upphædd er hægri enn saldo.');
        END IF;

        INSERT INTO loggur (
            konto_id,
            saldo_broyting,
            móttakari_id,
            tekst
        )
        VALUES (
            fra_id,
            -flyting,
            NULL,
            egintekst
        );

    ELSIF slag = 'FLYTING' THEN
        IF fra_id < til_id THEN
            SELECT saldo
            INTO fra_saldo
            FROM konto
            WHERE konto_id = fra_id
            FOR UPDATE;

            SELECT saldo
            INTO til_saldo
            FROM konto
            WHERE konto_id = til_id
            FOR UPDATE;
        ELSE
            SELECT saldo
            INTO til_saldo
            FROM konto
            WHERE konto_id = til_id
            FOR UPDATE;

            SELECT saldo
            INTO fra_saldo
            FROM konto
            WHERE konto_id = fra_id
            FOR UPDATE;
        END IF;

        IF flyting > fra_saldo THEN
            RAISE_APPLICATION_ERROR(-20004, 'ERROR: Flyting má ikki vera yvir saldo.');
        END IF;

        INSERT INTO loggur (
            konto_id,
            saldo_broyting,
            móttakari_id,
            tekst
        )
        VALUES (
            fra_id,
            -flyting,
            til_id,
            egintekst
        );

        INSERT INTO loggur (
            konto_id,
            saldo_broyting,
            móttakari_id,
            tekst
        )
        VALUES (
            til_id,
            flyting,
            fra_id,
            mottokutekst
        );

    ELSE
        RAISE_APPLICATION_ERROR(-20006, 'ERROR: Ókent slag á kladdu.');
    END IF;

    UPDATE kladda
    SET status = 'BOKAD',
        bokad_av_p_id = brukari_p_id,
        bokad_dato = SYSDATE
    WHERE kladdu_id = kladdu_id;

    COMMIT;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20005, 'ERROR: Starvsfólk, kladda ella konto fannst ikki.');
    WHEN OTHERS THEN
        RAISE;
END boka_kladdu;
/

CREATE OR REPLACE PROCEDURE avvisa_kladdu (
    brukari_p_id IN NUMBER,
    kladdu_id        IN NUMBER
) IS
    atgongd starvsfolk.atgongd_typa%TYPE;
BEGIN
    SELECT atgongd_typa
    INTO atgongd
    FROM starvsfolk
    WHERE p_id = brukari_p_id;

    IF atgongd != 'STARVSFOLK' AND atgongd != 'ADMIN' THEN
        RAISE_APPLICATION_ERROR(-20001, 'ERROR: Bert starvsfólk ella admin kunnu avvísa.');
    END IF;

    UPDATE kladda
    SET status = 'AVVIST',
        bokad_av_p_id = brukari_p_id,
        bokad_dato = SYSDATE
    WHERE kladdu_id = kladdu_id
      AND status = 'OAVGJORD';

    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'ERROR: Kladdan finst ikki ella er longu viðgjørd.');
    END IF;

    COMMIT;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERROR: Starvsfólk fannst ikki.');
    WHEN OTHERS THEN
        RAISE;
END avvisa_kladdu;
/
