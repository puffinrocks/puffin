INSERT INTO settings(`key`, `value`) VALUES 
('mail_host', 'mail'),
('mail_port', '25');

UPDATE settings SET value='smtp' WHERE `key` = 'mail_driver';


