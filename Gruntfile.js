module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    sass: {                              // Task
      dist: {                            // Target
        options: {                       // Target options
          style: 'expanded'
        },
        files: {                         // Dictionary of files
          'static/css/style.css': 'src/css/home-style.scss',       // 'destination': 'source'
          'static/css/bootstrap.min.css': 'src/css/bootstrap.scss',       // 'destination': 'source'
          'static/css/jquery.colorbox.min.css': 'src/css/jquery.colorbox.scss',       // 'destination': 'source'
        }
      }
    },
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['src/**/*.js'],
        dest: 'static/<%= pkg.name %>.js'
      }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n'
      },
      dist: {
      src: 'src/js/bootstrap.js',
      dest: 'static/js/bootstrap.min.js'
      }
    },
    qunit: {
      files: ['test/**/*.html']
    },
    jshint: {
      files: ['Gruntfile.js', 'src/**/*.js', 'static/**/*.js'],
      options: {
        //这里是覆盖JSHint默认配置的选项
        globals: {
          jQuery: true,
          console: true,
          module: true,
          document: true
        }
      }
    },

    watch: {
       // scripts: {
       //  files: '**/*.js',
       //  tasks: 'jshint',
       //  options: {
       //    livereload: true,
       //  },
       // },
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
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-qunit');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');

  grunt.registerTask('test', ['jshint', 'qunit']);

  grunt.registerTask('default', ['sass', 'uglify']);

};