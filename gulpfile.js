const { src, dest, parallel, watch } = require('gulp')
const sass = require('gulp-sass')
const postcss = require('gulp-postcss')
const concat = require('gulp-concat')
const babel = require('gulp-babel')
const uglify = require('gulp-uglify')
const autoprefixer = require('autoprefixer')

const static_root = 'libraries/libraries/static'
const settings = {

	/**
	 * Distribution settings
	 */
	dist: {
		css: static_root + '/css/',
		js: static_root + '/js/'
	},

	/**
	 * Source settings
	 */

	src: {
		exhibits: [static_root + '/js/exhibits.js'],
		js: [static_root + '/js/src/*.js'],
		main: [static_root + '/scss/main.scss', static_root + '/scss/exhibits.scss'],
		scss: [static_root + '/scss/**/*.scss']
	}
};

// tasks for each major set of files (main site CSS, main site JS, exhibits JS)
function allCSS () {
	return src(settings.src.main, { sourcemaps: true })
		.pipe(sass({ outputStyle: 'compressed' }).on('error', sass.logError))
		.pipe(postcss([ autoprefixer({ browsers: ['last 2 versions'] }) ]))
		.pipe(dest(settings.dist.css));
}

function mainJS () {
	return src(settings.src.js, { sourcemaps: true })
		.pipe(concat('main.min.js'))
		.pipe(babel({ presets: ['@babel/preset-env'] }))
		.pipe(uglify())
		.pipe(dest(settings.dist.js));
}

function exhibitsJS() {
	return src(settings.src.exhibits, { sourcemaps: true })
		.pipe(concat('exhibits.min.js'))
		.pipe(babel({ presets: ['@babel/preset-env'] }))
		.pipe(uglify())
		.pipe(dest(settings.dist.js));
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
