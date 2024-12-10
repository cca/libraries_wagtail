const globals = require('globals')
const js = require("@eslint/js")

module.exports = [
    js.configs.recommended,
    // "global" ignores must be alone in a config object
    // https://eslint.org/docs/latest/use/configure/configuration-files#globally-ignoring-files-with-ignores
    {ignores: ["**/*.min.js"]},
    // client-side js for the website
    {
        files: ["libraries/**/*.js"],
        languageOptions: {
            ecmaVersion: 2022,
            globals: {
                ...globals.browser,
                angular: 'readonly',
                jQuery: 'readonly',
                $: 'readonly',
            },
            sourceType: "script"
        },
        name: "wagtail browser js",
        rules: {
            indent: [ 'warn', 4 ],
            'linebreak-style': [ 'error', 'unix' ],
        }
    },
    // scripts run via node
    {
        files: ["eslint.config.js", "gulpfile.js"],
        languageOptions: {
            ecmaVersion: 2022,
            globals: {
                ...globals.commonjs,
            },
            sourceType: "commonjs"
        },
        name: "repo node js",
    },
]
