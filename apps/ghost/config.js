var path = require('path'),
    config;

config = {

    development: {
        url: 'http://' + process.env.VIRTUAL_HOST,
        
        // Visit http://support.ghost.org/mail for instructions
        mail: {
            transport: 'SMTP',
            options: {
                host: 'mail',
                port: 25
            },
        },
        
        database: {
            client: 'sqlite3',
            connection: {
                filename: path.join(process.env.GHOST_CONTENT, '/data/ghost.db')
            },
            debug: false
        },

        server: {
            host: '0.0.0.0',
            port: '2368'
        },

        paths: {
            contentPath: path.join(process.env.GHOST_CONTENT, '/')
        }
    }

};

module.exports = config;

