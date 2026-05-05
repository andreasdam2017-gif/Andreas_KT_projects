DROP TABLE loggur;
DROP TABLE kladda;
DROP TABLE starvsfolk;
DROP TABLE børn;
DROP TABLE hjúnaband;
DROP TABLE konto;
DROP TABLE kundi;
DROP TABLE kontoslag;
DROP TABLE pers;
DROP TABLE bústað;
DROP TABLE postkota;



CREATE TABLE postkota (
    postkota NUMBER PRIMARY KEY,
    bygd VARCHAR(20)
);

CREATE TABLE bústað (
    bústað_id NUMBER PRIMARY KEY,
    postkota NUMBER,
    gøta VARCHAR2(40),
    húsnummar NUMBER,
    hædd NUMBER,
    rúmnummar NUMBER,
    CONSTRAINT fk_postkota
        FOREIGN KEY (postkota) REFERENCES postkota(postkota)
);

CREATE TABLE pers (
    p_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    p_tal VARCHAR2(11) UNIQUE NOT NULL,
    fornavn VARCHAR2(40),
    eftirnavn VARCHAR2(40),
    føðingardag VARCHAR2(8) DEFAULT '01010000' NOT NULL,
    kyn varchar2(1) DEFAULT 'm' NOT NULL,
    CONSTRAINT chk_kyn CHECK (kyn IN ('m', 'k')),
    bústað_id NUMBER,
    CONSTRAINT fk_bústað_id
        FOREIGN KEY (bústað_id) REFERENCES bústað(bústað_id),
    CONSTRAINT chk_fodingardag
        CHECK (REGEXP_LIKE(føðingardag, '^[0-9]{8}$'))
);
CREATE TABLE kundi (
    kunda_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stovningar_dato date DEFAULT sysdate not null,
    slett_dato date,
    loynuorð varchar2(40),
    p_id number,
    CONSTRAINT fk_konto_eigari
            FOREIGN KEY (p_id) REFERENCES pers(p_id)
);

CREATE TABLE kontoslag (
    kontoslag_id VARCHAR2(3) PRIMARY KEY,
    slag_navn varchar2(40),
    credit_renta NUMBER(4,3),
    debit_renta NUMBER(4,3)
);

CREATE TABLE konto (
    konto_id VARCHAR2(11) DEFAULT '0' PRIMARY KEY,
    saldo NUMBER(12,2),
    kontotypa varchar2(3),
    eigari_p_id NUMBER,
    CONSTRAINT fk_konto_kundi
        FOREIGN KEY (eigari_p_id) REFERENCES kundi(kunda_id),
    CONSTRAINT fk_kontoslag
        FOREIGN KEY (kontotypa) REFERENCES kontoslag(kontoslag_id)
);

CREATE TABLE hjúnaband (
    hjúnaband_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    p1_id NUMBER NOT NULL,
    p2_id NUMBER NOT NULL,
    gift_dato DATE DEFAULT SYSDATE NOT NULL,
    skild_dato DATE,
    CONSTRAINT fk_hjúnaband_p1
        FOREIGN KEY (p1_id) REFERENCES pers(p_id),
    CONSTRAINT fk_hjúnaband_p2
        FOREIGN KEY (p2_id) REFERENCES pers(p_id),
    CONSTRAINT chk_hjúnaband_ikki_sami
        CHECK (p1_id != p2_id),
    CONSTRAINT chk_hjúnaband_rað
        CHECK (p1_id < p2_id),
    CONSTRAINT chk_hjúnaband_dato
        CHECK (skild_dato IS NULL OR skild_dato >= gift_dato)
);

CREATE UNIQUE INDEX hjúnaband_aktivt_par
    ON hjúnaband (
        CASE WHEN skild_dato IS NULL THEN p1_id END,
        CASE WHEN skild_dato IS NULL THEN p2_id END
    );

CREATE TABLE starvsfolk (
    p_id number PRIMARY KEY,
    starv_navn VARCHAR2(20) NOT NULL,
    lon NUMBER,
    atgongd_typa VARCHAR2(20) DEFAULT 'ONEYDUGT' NOT NULL,

    CONSTRAINT fk_starvsfolk_p_id
        FOREIGN KEY (p_id) REFERENCES pers(p_id),

    CONSTRAINT chk_atgongd_typa
            CHECK (atgongd_typa IN ('ONEYDUGT', 'STARVSFOLK', 'ADMIN'))
);
CREATE TABLE børn (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    p1_id NUMBER NOT NULL,
    p2_id NUMBER,
    barn_id NUMBER NOT NULL,
    CONSTRAINT fk_born_p1
        FOREIGN KEY (p1_id) REFERENCES pers(p_id),
    CONSTRAINT fk_born_p2
        FOREIGN KEY (p2_id) REFERENCES pers(p_id),
    CONSTRAINT fk_born_barn
        FOREIGN KEY (barn_id) REFERENCES pers(p_id),
    CONSTRAINT uq_born_barn
        UNIQUE (barn_id),
    CONSTRAINT chk_born_p1_barn
        CHECK (p1_id != barn_id),
    CONSTRAINT chk_born_p2_barn
        CHECK (p2_id IS NULL OR p2_id != barn_id),
    CONSTRAINT chk_born_p1_p2
        CHECK (p2_id IS NULL OR p1_id != p2_id)
);

CREATE TABLE kladda (
    kladdu_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    flyting NUMBER(12,2) NOT NULL,
    frá_id VARCHAR2(11),
    til_id VARCHAR2(11),
    egintekst VARCHAR2(160),
    mottokutekst VARCHAR2(160),
    bokad_av_p_id NUMBER,
    bokad_dato DATE,
    slag VARCHAR2(20) NOT NULL,
    status VARCHAR2(20) DEFAULT 'OAVGJORD' NOT NULL,
    dato DATE DEFAULT SYSDATE NOT NULL,

    CONSTRAINT fk_kladda_fra
        FOREIGN KEY (frá_id) REFERENCES konto(konto_id),

    CONSTRAINT fk_kladda_til
        FOREIGN KEY (til_id) REFERENCES konto(konto_id),

    

    CONSTRAINT chk_kladda_flyting
        CHECK (flyting > 0),

    CONSTRAINT chk_kladda_slag
        CHECK (slag IN ('INNSETING', 'UTTOKA', 'FLYTING')),

    CONSTRAINT chk_kladda_status
        CHECK (status IN ('OAVGJORD', 'BOKAD', 'AVVIST')),

    CONSTRAINT chk_kladda_ikki_sama_konto
        CHECK (frá_id IS NULL OR til_id IS NULL OR frá_id != til_id),

    CONSTRAINT chk_kladda_slag_kontur
        CHECK (
            (slag = 'INNSETING' AND frá_id IS NULL AND til_id IS NOT NULL)
            OR
            (slag = 'UTTOKA' AND frá_id IS NOT NULL AND til_id IS NULL)
            OR
            (slag = 'FLYTING' AND frá_id IS NOT NULL AND til_id IS NOT NULL AND frá_id != til_id)
        )
);

CREATE TABLE loggur (
    log_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    konto_id VARCHAR2(11) NOT NULL,
    saldo_broyting NUMBER(12,2) NOT NULL,
    log_dato DATE DEFAULT SYSDATE NOT NULL,
    móttakari_id VARCHAR2(11),
    tekst VARCHAR2(160),
    leypandi_saldo number(12,2),
    CONSTRAINT fk_log_konto
        FOREIGN KEY (konto_id) REFERENCES konto(konto_id),
    CONSTRAINT fk_log_mottakari
        FOREIGN KEY (móttakari_id) REFERENCES konto(konto_id)
);

