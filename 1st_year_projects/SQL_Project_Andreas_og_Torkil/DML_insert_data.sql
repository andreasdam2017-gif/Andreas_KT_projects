
INSERT INTO postkota (postkota, bygd)
VALUES (100, 'Tórshavn');

INSERT INTO bústað (bústað_id, postkota, gøta, húsnummar, hædd, rúmnummar)
VALUES (1, 100, 'homeroad', 1, 1, 1);

INSERT INTO bústað (bústað_id, postkota, gøta, húsnummar, hædd, rúmnummar)
VALUES (2, 100, 'bankavegur', 1, 1, 1);


INSERT INTO pers (p_tal, fornavn, eftirnavn, føðingardag, kyn, bústað_id)
VALUES ('010101-123', 'Jón', 'Hansen', '25032000', 'm', 1);

INSERT INTO pers (p_tal, fornavn, eftirnavn, føðingardag, kyn, bústað_id)
VALUES ('020202-234', 'Maria', 'Joensen', '25032000', 'k', 1);

INSERT INTO pers (p_tal, fornavn, eftirnavn, føðingardag, kyn, bústað_id)
VALUES ('030303-345', 'Páll', 'Olsen', '25032000', 'm', 1);

INSERT INTO pers (p_tal, fornavn, eftirnavn, føðingardag, kyn, bústað_id)
VALUES ('040404-456', 'Anna', 'Petersen', '25032000', 'k', 1);

INSERT INTO pers (p_tal, fornavn, eftirnavn, føðingardag, kyn, bústað_id)
VALUES ('040404-456', 'Rob', 'Banks', '25032000', 'm', 2);


INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
VALUES ('000', 'konto_hja_bankanum', 0, 0);

INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
VALUES ('100', 'lán', 0.05, 0);

INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
VALUES ('200', 'nýtsla', 0.1, 0.005);

INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
VALUES ('300', 'uppsparing', 0.1, 0.01);

INSERT INTO kontoslag (kontoslag_id, slag_navn, credit_renta, debit_renta)
VALUES ('400', 'ódefinera', 0.1, 0);


INSERT INTO kundi (loynuorð, p_id)
VALUES ('gottloynuorð', 1);
INSERT INTO kundi (loynuorð, p_id)
VALUES ('gottloynuorð', 2);
INSERT INTO kundi (loynuorð, p_id)
VALUES ('gottloynuorð', 3);
INSERT INTO kundi (loynuorð, p_id)
VALUES ('gottloynuorð', 4);

INSERT INTO kundi (loynuorð, p_id)
VALUES ('go5145ttloy3nuorðrwqrycytigojuåp', 5);

INSERT INTO konto (konto_id, saldo, kontotypa, eigari_p_id)
VALUES ('69692000001', 0, '200', 1);
INSERT INTO konto (konto_id, saldo, kontotypa, eigari_p_id)
VALUES ('69692000002', 0, '200', 2);
INSERT INTO konto (konto_id, saldo, kontotypa, eigari_p_id)
VALUES ('69691000001', 0, '100', 3);
INSERT INTO konto (konto_id, saldo, kontotypa, eigari_p_id)
VALUES ('69692000003', 0, '200', 3);
INSERT INTO konto (konto_id, saldo, kontotypa, eigari_p_id)
VALUES ('69693000001', 0, '300', 4);
INSERT INTO konto (konto_id, saldo, kontotypa, eigari_p_id)
VALUES ('69693000002', 0, '400', 1);

INSERT INTO konto (konto_id, saldo, kontotypa, eigari_p_id)
VALUES ('69690000016', 0, '000', 5);

update konto
set saldo = 1000000000
where konto_id = 69690000016;






select kontoslag.slag_navn, konto.konto_id
from konto, kontoslag 
where kontotypa = kontoslag_id;