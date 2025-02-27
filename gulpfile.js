const { src, dest, parallel, watch } = require('gulp')
const sass = require('gulp-sass')(require('sass'))
const postcss = require('gulp-postcss')
const concat = require('gulp-concat')
const babel = require('gulp-babel')
const uglify = require('gulp-uglify')
const autoprefixer = require('autoprefixer')

const source = 'libraries/libraries/static'
// files will be copied both here _and_ above dir, too
const dist = 'libraries/static'

const settings = {
    dist: {
        css: dist + '/css/',
        js: dist + '/js/',
    },
    src: {
        // JavaScript src
        exhibits: [source + '/js/exhibits.js'],
        js: [source + '/js/src/*.js'],
        // SASS src
        styles: [
            source + '/scss/main.scss'
            , source + '/scss/exhibits.scss'
        ],
        scss: [
            source + '/scss/**/*.scss'
        ]
    }
}

// tasks for each major set of files (main site CSS, main site JS, exhibits JS)
function allCSS() {
    return src(settings.src.styles, { sourcemaps: true })
        .pipe(sass({ outputStyle: 'compressed' }).on('error', sass.logError))
        .pipe(postcss([ autoprefixer() ]))
        .pipe(dest(settings.dist.css))
        .pipe(dest('libraries/' + settings.dist.css))
}

function exhibitsJS() {
    return src(settings.src.exhibits, { sourcemaps: true })
        .pipe(concat('exhibits.min.js'))
        .pipe(babel({ presets: ['@babel/preset-env'] }))
        .pipe(uglify())
        .pipe(dest(settings.dist.js))
        .pipe(dest('libraries/' + settings.dist.js))
}

function mainJS() {
    return src(settings.src.js, { sourcemaps: true })
        .pipe(concat('main.min.js'))
        .pipe(babel({ presets: ['@babel/preset-env'] }))
        .pipe(uglify({ output: { comments: 'some' } }))
        .pipe(dest(settings.dist.js))
        .pipe(dest('libraries/' + settings.dist.js))
}

// watch each main set of files & run its associated task
function defaultTask() {
    watch(settings.src.exhibits, exhibitsJS)
    watch(settings.src.js, mainJS)
    watch(settings.src.scss, allCSS)
}

// expose all tasks
exports.js = mainJS
exports.css = allCSS
exports.exhibits = exhibitsJS
exports.build = parallel(allCSS, mainJS, exhibitsJS)
exports.default = defaultTask
