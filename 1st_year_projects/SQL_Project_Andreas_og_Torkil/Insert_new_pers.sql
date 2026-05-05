CREATE OR REPLACE PROCEDURE new_per (
    fornavn      IN VARCHAR2,
    eftirnavn    IN VARCHAR2,
    føðingardag  IN VARCHAR2,
    kyn          IN VARCHAR2,
    bústað_id    IN NUMBER
) IS
BEGIN
    IF føðingardag IS NULL OR LENGTH(føðingardag) <> 8 THEN
        RAISE_APPLICATION_ERROR(-20001, 'ERROR: Føðingardagur má vera DDMMYYYY.');
    END IF;

    IF kyn NOT IN ('m', 'k') THEN
        RAISE_APPLICATION_ERROR(-20002, 'ERROR: Kyn má vera m ella k.');
    END IF;

    IF ptal_gen(føðingardag, kyn) IS NULL THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERROR: Ógildugur føðingardagur.');
    END IF;

    INSERT INTO pers(fornavn, eftirnavn, føðingardag, kyn, bústað_id)
    VALUES (fornavn, eftirnavn, føðingardag, kyn, bústað_id);

EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
/
