# Google Groups Scraper

A tool for scraping thread titles and posts (articles) from historical Google Groups Usenet archives.

## Introduction
"scraper.py" is messy, uncommented, and only capable of scraping thread headers right now, but it's a start.

The script loads one week's worth of threads at a time and exports the thread title, URL, and other data to a JSON for that period. Unfortuantely, the process is quite slow because each page of thread results must be rendered with JavaScript in order for the content to be accessible via lxml. It took maybe 12 hours to load and extract content for ~160,000 thread titles from alt.conspiracy (my area of research interest).

## License

Google Groups Scraper
Copyright (C) 2018 Justin Parnell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for additional details.