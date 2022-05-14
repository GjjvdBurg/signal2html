# Changelog

## Version 0.2.9

* Fix bug in [#59](https://github.com/GjjvdBurg/signal2html/issues/59). Thanks 
  to aweinberg38 for reporting this issue and providing a patch.

## Version 0.2.8

* Code fixes for group update messages (thanks to @prgarnett and @aweinberg38 
  for reporting [#37](https://github.com/GjjvdBurg/signal2html/issues/57))

## Version 0.2.7

* Code fixes for missing message data

## Version 0.2.6

* Bugfix for handling mentions

## Version 0.2.5

* Add support for clickable urls (thanks to @sbaum for reporting 
  [#37](https://github.com/GjjvdBurg/signal2html/issues/37))
* Display more message metadata (thanks to @ericthegrey in 
  [#33](https://github.com/GjjvdBurg/signal2html/pull/33))
* Add header to threads as in the app (thanks to @Aztorius for suggesting this 
  in [#39](https://github.com/GjjvdBurg/signal2html/issues/39))
* Minor formatting fixes for thread messages

## Version 0.2.4

* Bugfix for resolving recipient names for database version 108 and higher 
  (thanks to @sbaum for reporting 
  [#34](https://github.com/GjjvdBurg/signal2html/issues/34)).

## Version 0.2.3

* Bugfix for non-existent recipients (thanks to @ericthegrey 
  [#30](https://github.com/GjjvdBurg/signal2html/issues/30)).
* Expand color palette to match Signal (thanks to @ChemoCosmo for reporting 
  this (see [#30](https://github.com/GjjvdBurg/signal2html/issues/30)).
* Support messages for video calls and key change (thanks to @ericthegrey 
  [#29](https://github.com/GjjvdBurg/signal2html/pull/29)).

## Version 0.2.2

* Add support for mentions (thanks to @ericthegrey)
* Fixes for output filenames and directories
* Minor cleanup

## Version 0.2.1

* Improve version tests (thanks to @ericthegrey)
* Add support for reactions (thanks to @ericthegrey)

## Version 0.2.0

* Clean up code using an Addressbook class for recipients (thanks to 
  @ericthegrey [#15](https://github.com/GjjvdBurg/signal2html/pull/15)).

## Version 0.1.8

* Add a fallback to download attachment of that are not image/audio/video, and 
  add support for showing stickers 
  ([#11](https://github.com/GjjvdBurg/signal2html/pull/11) thanks to 
  @ericthegrey)

## Version 0.1.7

* Add phone field for quote author (bugfix)

## Version 0.1.6

* Use thread-specific filenames
  ([#10](https://github.com/GjjvdBurg/signal2html/pull/10) thanks to 
  @ericthegrey)

## Version 0.1.5

* Add dataclasses dependency for python 3.6

## Version 0.1.4

* Replace absolute URLs for attachments with relative ones.

## Version 0.1.3

* Fix fallback for recipient name (thanks to @Otto-AA!)
* Add several mime-types to HTML template
* Bugfix for recipient names and group detection
  ([issue #5](https://github.com/GjjvdBurg/signal2html/issues/5))

## Version 0.1.2

* Add support for more recent database versions
* Move each thread to a separate folder in output directory
* Copy attachments to the thread directory

## Version 0.1.1

* Minor fixes (encoding, unknown quoted authors)

## Version 0.1.0

* Initial release
