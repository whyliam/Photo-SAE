//包含gulp   
var gulp = require('gulp');  

//包含我们的插件   

var sass = require('gulp-ruby-sass'),
    autoprefixer = require('gulp-autoprefixer'),
    minifycss = require('gulp-minify-css'),
    jshint = require('gulp-jshint'),
    uglify = require('gulp-uglify'),
    imagemin = require('gulp-imagemin'),
    rename = require('gulp-rename'),
    concat = require('gulp-concat'),
    notify = require('gulp-notify'),
    cache = require('gulp-cache'),
    livereload = require('gulp-livereload');

//编译sass  

gulp.task('styles', function() {
  return gulp.src('./src/scss/style.scss')
    .pipe(sass({ style: 'compressed', 'sourcemap=none': true, 'compass': true }))
    .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4'))
    .pipe(rename({suffix: '.min'}))
    .pipe(gulp.dest('./site/static/css'))
    .pipe(notify({ message: 'Styles task complete' }));
});

//拼接、简化JS文件   

gulp.task('scripts', function() {
  return gulp.src('./src/js/*.js')
    .pipe(jshint('.jshintrc'))
    .pipe(jshint.reporter('default'))
    .pipe(concat('main.js'))
    .pipe(gulp.dest('./site/static/js'))
    .pipe(rename({suffix: '.min'}))
    .pipe(uglify())
    .pipe(gulp.dest('./site/static/js'))
    .pipe(notify({ message: 'Scripts task complete' }));
});

//压缩图片

gulp.task('images', function() {
  return gulp.src('./src/images/*')
    // .pipe(imagemin({ optimizationLevel: 3, progressive: true, interlaced: true }))
    .pipe(cache(imagemin({ optimizationLevel: 5, progressive: true, interlaced: true })))
    .pipe(gulp.dest('./site/static/imgs'))
    .pipe(notify({ message: 'Images task complete' }));
});


//默认任务   
gulp.task('default',function(){
    gulp.run('styles','scripts','images');

    //监视我们JS文件的变化   
    gulp.task('watch', function() {
        // Watch .scss files
        gulp.watch('src/scss/*.scss', ['styles']);
        // Watch .js files
        gulp.watch('src/js/*.js', ['scripts']);
        // Watch image files
        gulp.watch('src/images/*', ['images']);
    });

    livereload.listen();
    gulp.watch(['site/**']).on('change', livereload.changed);
});  