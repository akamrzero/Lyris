pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'src'
gnome = import('gnome')


python = import('python')
py3 = python.find_installation('python3')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'lyris.in',
  output: 'lyris',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

lyris_sources = [
  'audioplayer.py',
  '__init__.py',
  'main.py',
  'queue.py',
  'window.py',
  'mpris.py',
]

install_data(lyris_sources, install_dir: moduledir)
install_subdir('utils', install_dir: moduledir)
install_subdir('widgets', install_dir: moduledir)
install_subdir('models', install_dir: moduledir)
