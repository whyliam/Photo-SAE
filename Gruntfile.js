module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: { // Task
            dist: { // Target
                options: { // Target options
                    style: 'expanded'
                },
                files: { // Dictionary of files
                    'site/static/css/style.css': 'src/css/style.scss', // 'destination': 'source'
                    'site/static/css/bootstrap.min.css': 'src/css/bootstrap.scss', // 'destination': 'source'
                }
            }
        },
        jshint: {
            options: {
                jshintrc: '.jshintrc'
            },
            files: ['Gruntfile.js', 'src/**/*.js']
        },
        uglify: {
            my_target: {
                files: {
                    'site/static/js/newpost.upload.min.js': ['src/js/newpost.upload.js']
                }
            }
        },

        watch: {
            scripts: {
                files: 'src/**/*.js',
                tasks: ['jshint','uglify'],
                options: {
                    livereload: true,
                },
            },
            css: {
                files: 'src/**/*.scss',
                tasks: ['sass'],
                options: {
                    livereload: true,
                },
            },
        }
    });

    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-qunit');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    grunt.registerTask('test', ['jshint', 'sass']);
    grunt.registerTask('default', ['sass', 'uglify']);

};
