'use strict';
const gulp = require('gulp');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename');
const postcss = require('gulp-postcss');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
const autoprefixer = require('autoprefixer');
const config = require('config');

const settings = {

	/**
	 * Distribution settings
	 */
	dist: {
		css: 'libraries/libraries/static/css/',
		js: 'libraries/libraries/static/js/'
	},

	/**
	 * Source settings
	 */
	src: {
		main: 'libraries/libraries/static/scss/main.scss',
		scss: ['libraries/libraries/static/scss/**/*.scss']
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
	const scriptsInConfig = config.get('scripts').map((name) => `src${name}`);
	// Assume this is always run in NODE_ENV=development
	console.log('Scripts that are bundled:\n',
		scriptsInConfig.join('\n'));
	gulp.src(scriptsInConfig)
		.pipe(sourcemaps.init())
		.pipe(concat('bundle.js'))
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
