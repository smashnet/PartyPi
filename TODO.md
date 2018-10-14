# Todo

## General

* make texts variable
* integrate partypi version in DB and implement DB mirgration for updates where necessary

## Photos

* photos overview page
  * show thumbnails of all photos (512px width)
  * full size on click
  * guess uploader by matching uploader-ip with subscriber-ip
* photos admin page (like overview, plus:)
  * button to delete single photo
  * make photos selectable
    * delete selected
  * select all button

## Subscribers

* subscriptions admin page
  * copy-to-clipboard-button for mail address
  * delete subscription button
  * clear all button
  * mailto: button with subscribers in bcc

## RESTful implementation

* Upload new photo
  * POST /photo
* Get photo by ID
  * GET /photo/{uuid}
* Get list of photos
  * GET /photos
* New subscriber
  * POST /subscription
* Get subscriber by ID
  * GET /subscription/{uuid}
* Get list of subscriptions
  * GET /subscriptions

Done
===========================

* store images with {uuid}.jpg on disc, and save filename in db
* generaliza front page image
