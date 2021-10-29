const { src, dest, parallel, watch } = require('gulp')
const sass = require('gulp-sass')(require('node-sass'))
const postcss = require('gulp-postcss')
const concat = require('gulp-concat')
const babel = require('gulp-babel')
const uglify = require('gulp-uglify')
const autoprefixer = require('autoprefixer')

const static_root = 'libraries/libraries/static'
const settings = {
	dist: {
		css: static_root + '/css/',
		js: static_root + '/js/'
	},
	src: {
		// JavaScript src
		exhibits: [static_root + '/js/exhibits.js'],
		js: [static_root + '/js/src/*.js'],
		summon: [static_root + '/summon/*.js'],
		// SASS src
		styles: [
			static_root + '/scss/main.scss'
			, static_root + '/scss/exhibits.scss'
			, static_root + '/summon/scss/summon.scss'
		],
		scss: [
			static_root + '/scss/**/*.scss',
			static_root + '/summon/scss/*.scss'
		]
	}
}

// tasks for each major set of files (main site CSS, main site JS, exhibits JS)
function allCSS() {
	return src(settings.src.styles, { sourcemaps: true })
		.pipe(sass({ outputStyle: 'compressed' }).on('error', sass.logError))
		.pipe(postcss([ autoprefixer() ]))
		.pipe(dest(settings.dist.css))
}

function mainJS() {
	return src(settings.src.js, { sourcemaps: true })
		.pipe(concat('main.min.js'))
		.pipe(babel({ presets: ['@babel/preset-env'] }))
		.pipe(uglify({ output: { comments: 'some' } }))
		.pipe(dest(settings.dist.js))
}

function exhibitsJS() {
	return src(settings.src.exhibits, { sourcemaps: true })
		.pipe(concat('exhibits.min.js'))
		.pipe(babel({ presets: ['@babel/preset-env'] }))
		.pipe(uglify())
		.pipe(dest(settings.dist.js))
}

function summonJS() {
	return src(settings.src.summon, { sourcemaps: true })
		.pipe(concat('summon.min.js'))
		.pipe(babel({ presets: ['@babel/preset-env'] }))
		.pipe(uglify())
		.pipe(dest(settings.dist.js))
}

// watch each main set of files & run its associated task
function defaultTask() {
	watch(settings.src.exhibits, exhibitsJS)
	watch(settings.src.js, mainJS)
	watch(settings.src.js, summonJS)
	watch(settings.src.scss, allCSS)
}

// expose all tasks
exports.js = mainJS
exports.css = allCSS
exports.exhibits = exhibitsJS
exports.build = parallel(allCSS, mainJS, exhibitsJS, summonJS)
exports.default = defaultTask
