CREATE TABLE IF NOT EXISTS vagas(
    id_vagas INTEGER PRIMARY KEY,
    cargo_vagas TEXT NOT NULL,
    requisitos_vagas TEXT NOT NULL, 
    salario_vagas REAL NOT NULL, 
    local_vagas TEXT NOT NULL, 
    email_vagas TEXT NOT NULL, 
    img_vagas TEXT NOT NULL
);