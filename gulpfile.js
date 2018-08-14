'use strict';
const gulp = require('gulp');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');
const postcss = require('gulp-postcss');
const concat = require('gulp-concat');
const babel = require('gulp-babel');
const uglify = require('gulp-uglify');
const autoprefixer = require('autoprefixer');

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

function styles () {
	gulp.src(settings.src.main)
		.pipe(sourcemaps.init())
		.pipe(sass({ outputStyle: 'compressed' }).on('error', sass.logError))
		.pipe(postcss([ autoprefixer({ browsers: ['last 2 versions'] }) ]))
		.pipe(sourcemaps.write('.'))
		.pipe(gulp.dest(settings.dist.css));
}
gulp.task('styles', styles);

function scripts () {
	gulp.src(settings.src.js)
		.pipe(sourcemaps.init())
		.pipe(concat('main.min.js'))
		.pipe(babel({ presets: ['env'] }))
		.pipe(uglify())
		.pipe(sourcemaps.write('.'))
		.pipe(gulp.dest( settings.dist.js ));

	gulp.src(settings.src.exhibits)
		.pipe(sourcemaps.init())
		.pipe(concat('exhibits.min.js'))
		.pipe(babel({ presets: ['env'] }))
		.pipe(uglify())
		.pipe(sourcemaps.write('.'))
		.pipe(gulp.dest( settings.dist.js ));
}
gulp.task('scripts', scripts);

/**
 * Build does not comb your code
 */
gulp.task('build', ['styles', 'scripts']);

gulp.task('default', function() {
	gulp.watch(settings.src.scss
		.concat(settings.src.js)
		.concat(settings.src.exhibits),
	['build'])
});
