'use strict';
const gulp = require('gulp');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename');
const postcss = require('gulp-postcss');
const concat = require('gulp-concat');
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
		js: [static_root + '/js/main.js'],
		main: static_root + '/scss/main.scss',
		scss: [static_root + '/scss/**/*.scss']
	}
};

gulp.task('watch', function() {
	gulp.watch(settings.src.scss, styles)
});

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
		.pipe(uglify())
		.pipe(sourcemaps.write('.'))
		.pipe(gulp.dest( settings.dist.js ));
}
gulp.task('scripts', scripts);

/**
 * Build does not comb your code
 */
gulp.task('build', ['styles', 'scripts']);

gulp.task('default', ['styles', 'watch']);
