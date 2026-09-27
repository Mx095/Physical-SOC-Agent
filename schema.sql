CREATE DATABASE IF NOT EXISTS physical_soc;
USE physical_soc;

CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,      -- 'session_lock', 'second_face'
    severity VARCHAR(20) NOT NULL,        -- 'info', 'warning', 'critical'
    description VARCHAR(255),
    snapshot_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
