CREATE OR REPLACE PROCEDURE new_starv (
    brukari_p_id   IN NUMBER, -- Er admin sum loggar inn
    p_id         IN NUMBER,   -- er nýggji starvsfólk
    starv_navn   IN VARCHAR2,
    lon          IN NUMBER
) IS
    brukari_atgongd  starvsfolk.atgongd_typa%TYPE;
    dummy          NUMBER;
BEGIN
    IF lon <= 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'ERROR: Løn má vera yvir 0');
    END IF;

    SELECT atgongd_typa
    INTO brukari_atgongd
    FROM starvsfolk
    WHERE p_id = brukari_p_id;

    IF brukari_atgongd <> 'ADMIN' THEN
        RAISE_APPLICATION_ERROR(-20002, 'ERROR: Bert administrator kann stovna starvsfólk.');
    END IF;

    SELECT p_id
    INTO dummy
    FROM pers
    WHERE p_id = p_id;

    INSERT INTO starvsfolk (starv_navn, lon, p_id)
    VALUES (starv_navn, lon, p_id);


EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERROR: Annaðhvørt er aktørurin ikki starvsfólk, ella persónurin er ikki til.');
    WHEN DUP_VAL_ON_INDEX THEN
        RAISE_APPLICATION_ERROR(-20004, 'ERROR: Hesin persónur er longu skrásettur sum starvsfólk.');
    WHEN OTHERS THEN
        RAISE;
END;
/

-- Rolle broytari er fyri at broyta rolluna hjá starvfólkum, har ein admin kann broyta løn,
-- Starv navn, access typa og meira
CREATE OR REPLACE PROCEDURE rolle_broytari ( 
    brukari_p_id IN NUMBER,
    p_id         IN NUMBER,
    starv_navn       IN VARCHAR2,
    lon              IN NUMBER,
    atgongd_typa     IN VARCHAR2
) IS
    brukari_atgongd  starvsfolk.atgongd_typa%TYPE;
    dummy            NUMBER;
BEGIN
    SELECT atgongd_typa
    INTO brukari_atgongd
    FROM starvsfolk
    WHERE p_id = brukari_p_id;

    IF brukari_atgongd <> 'ADMIN' THEN
        RAISE_APPLICATION_ERROR(-20002, 'ERROR: Bert administrator kann broyta starvsfólk.');
    END IF;

    SELECT p_id
    INTO dummy
    FROM starvsfolk
    WHERE p_id = p_id;

    IF lon IS NOT NULL THEN
        IF lon <= 0 THEN
            RAISE_APPLICATION_ERROR(-20001, 'ERROR: Løn má vera yvir 0.');
        END IF;
    END IF;

    IF atgongd_typa IS NOT NULL THEN
        IF atgongd_typa NOT IN ('ONEYDUGT', 'STARVSFOLK', 'ADMIN') THEN
            RAISE_APPLICATION_ERROR(-20005, 'ERROR: Ógildig atgongd_typa.');
        END IF;
    END IF;

    IF starv_navn IS NOT NULL THEN
        UPDATE starvsfolk
        SET starv_navn = starv_navn
        WHERE p_id = p_id;
    END IF;

    IF lon IS NOT NULL THEN
        UPDATE starvsfolk
        SET lon = lon
        WHERE p_id = p_id;
    END IF;

    IF atgongd_typa IS NOT NULL THEN
        UPDATE starvsfolk
        SET atgongd_typa = atgongd_typa
        WHERE p_id = p_id;
    END IF;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERROR: Annaðhvørt finst broytarin ikki sum starvsfólk, ella finst starvsfólkið ikki.');
    WHEN OTHERS THEN
        RAISE;
END rolle_broytari;
/
    