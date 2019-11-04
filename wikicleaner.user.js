// ==UserScript==
// @name           WikiCleaner
// @namespace      joeytwiddle
// @description    Four visual improvements for Wikipedia (and other wikis):  Indents sub-sections to make the layout clearer.  Hides the sidebar (toggle by clicking the header).  Floats the Table of Contents for access when scrolled.  Converts heading underlines to overlines.
// @downstreamURL  http://userscripts.org/scripts/source/60832.user.js
// @version        1.0.0
// @include        *wiki*
// @include        http://www.buzztard.com/*
// @include        http://encyclopediadramatica.com/*
// @include        http://www.wormus.com/leakytap/*
// @include        http://theinfosphere.org/*
// @include        http://rosettacode.org/mw/*
// @grant          GM_setValue
// @grant          GM_addStyle
// @grant          GM_getValue
// @grant          GM_log
// ==/UserScript==

// Without this function wrapper, Mozilla Firefox rejects the whole script, because it sees the top-level 'return;' as invalid syntax!

(function(){

// Feature #1 : Make the sidebar collapsible so the page content can fill the whole width.

var toggleSidebar = true;

var minimisedSidebarSize = 10;

// When opening the sidebar again, the transition displays the sidebar contents
// before there is space for it, causing brief ugly overlap!  So we delay
// unhiding to look prettier.
// CONSIDER: Perhaps this could look even smoother if the text appeared/disappeared using opacity.
var delayHide = 0;
var delayUnhide = ( document.getElementById("mw-panel") ? 250 : 0 );

var debug = false;



/* CONSIDER: As we scroll the page, light up the "current" section in the TOC.
 *
 * FIXED: One occasional problem with the TOC is when it is taller than the
 *      window!  (I usually work around this by zooming out (reducing font
 *      size), but perhaps we can use CSS overflow to solve it properly.)
 *
 * TODO: Indentation was not working well in edit preview on Hwiki(MW).
*/

/* Changelog
 *  5/ 2/2012 - Better (though more fragile) click-to-toggle areas.
 *  3/ 1/2012 - Fixed Chrome compatibility so it works!  Doh.
 * 23/ 3/2011 - Added Chrome compatibility.
*/

// Recent versions do not play nice together, so just in case we run WI twice:
if (unsafeWindow.WikiIndent_loaded) {
	return;
} else {
	unsafeWindow.WikiIndent_loaded = true;
}

function log(x) {
	x = "[WI] "+x;
	if (this.GM_log) {
		this.GM_log(x);
	} else if (this.console && console.log) {
		console.log(x);
	} else {
		window.status = ""+x;
		// alert(x);
	}
}

// For bookmarklets:
if (typeof GM_addStyle == "undefined") {
	GM_addStyle = function(css) {
		var head, style;
		head = document.getElementsByTagName("head")[0];
		if (!head) { return; }
		style = document.createElement("style");
		style.type = "text/css";
		style.innerHTML = css;
		head.appendChild(style);
	};
}

if (typeof GM_setValue == 'undefined' || window.navigator.vendor.match(/Google/)) {
	GM_log("WikiIndent: Adding fallback implementation of GM_set/getValue");

	if (typeof localStorage == 'undefined') {

		GM_getValue = function(name, defaultValue) {
			return defaultValue;
		};

	} else {

		GM_setValue = function(name, value) {
			value = (typeof value)[0] + value;
			localStorage.setItem(name, value);
		};

		GM_getValue = function(name, defaultValue) {
			var value = localStorage.getItem(name);
			if (!value) {
				return defaultValue;
            }
			var type = value[0];
			value = value.substring(1);
			switch (type) {
				case 'b':
					return value == 'true';
				case 'n':
					return Number(value);
				default:
					return value;
			}
		};

	}

}


// == Main == //

function doIt() {



	//// Feature #1 : Hide the sidebar.  Fullsize the content.

	// Toggle the sidebar by clicking the "page background" (empty space outside
	// the main content).  Sometimes clicking the content background is enough.

	if (toggleSidebar) {

		var content = document.getElementById("content")
			|| document.getElementById("column-content");
		var sideBar = document.getElementById("column-one")
			|| document.getElementById("panel")
			|| /* WikiMedia: */ document.getElementById("mw-panel")
			|| /* forgot:    */ document.getElementById("jq-interiorNavigation")
			|| /* pmwiki:    */ document.getElementById('wikileft');
		var toToggle = [
            document.getElementById("page-base"),
            document.getElementById("siteNotice"),
            document.getElementById("head"),
            document.getElementById("mw-head"),
            document.getElementById("mw-page-base"),
            document.getElementById("footer"),
            document.getElementById("toctitle"),
            ...document.getElementsByClassName("toctitle"),
            ...document.getElementsByClassName("mw-editsection"),
        ];
		var cac = document.getElementById("p-cactions");
		var cacOldHome = ( cac ? cac.parentNode : null );

		function toggleWikipediaSidebar(evt) {

			// We don't want to act on all clicked body elements (notably not the WP
			// image).  I detected two types of tag we wanted to click.
			/*if (!evt || evt.target.tagName == "UL" || evt.target.tagName == "DIV") {*/

			// That was still activating on divs in the content!  (Gaps between paragraphs.)
			// This only acts on the header area.
			var thisElementTogglesSidebar;
			var inStartup = (evt == null);
			if (inStartup) {
				thisElementTogglesSidebar = true;
			} else {
				var elem = evt.target;
				var clickedHeader = (elem.id == 'mw-head');
				// For wikia.com:
				clickedHeader |= (elem.id=="WikiHeader");
				// For Wikimedia:
				var clickedPanelBackground = elem.id == 'mw-panel' || elem.className.indexOf('portal')>=0;
				clickedPanelBackground |= elem.id == 'column-content'; // for beebwiki (old mediawiki?)
				// Hopefully for sites in general.  Allow one level below body.  Needed for Wikia's UL.
				var clickedAreaBelowSidebar = (elem.tagName == 'HTML' || elem.tagName == 'BODY');
				var clickedBackground = (elem.parentNode && elem.parentNode.tagName == "BODY");
				thisElementTogglesSidebar = clickedHeader || clickedPanelBackground || clickedAreaBelowSidebar || clickedBackground;
			}
			if (thisElementTogglesSidebar) {

				if (evt){
					evt.preventDefault();
                }
				if (debug) { GM_log("evt=",evt); }
				// if (evt) GM_log("evt.target.tagName="+evt.target.tagName);
				/* We put the GM_setValue calls on timers, so they won't slow down the rendering. */
				// Make the change animate smoothly:
				content.style.transition = 'all 150ms ease-in-out';
				if (sideBar) {
					if (sideBar.style.display == '') {
						// Wikipedia's column-one contains a lot of things we want to hide
						sideBar.style.display = 'none';
						if (content) {
							content.oldMarginLeft = content.style.marginLeft;
                            content.oldMarginTop = content.style.marginTop;
                            content.oldMarginBottom = content.style.marginBottom;
							content.style.marginLeft = minimisedSidebarSize+'px';
                            content.style.marginTop = minimisedSidebarSize+'px';
                            content.style.marginBottom = minimisedSidebarSize+'px';
						}
						for (var i in toToggle) {
							if (toToggle[i]) { toToggle[i].style.display = 'none'; }
						}
						// but one of them we want to preserve
						// (the row of tools across the top):
						if (cac){
							sideBar.parentNode.insertBefore(cac,sideBar.nextSibling);
                        }
						setTimeout(function(){
							GM_setValue("sidebarVisible",false);
						},200);
					} else {
						function unhide() {
							sideBar.style.display = '';
						}
						setTimeout(unhide,delayUnhide);
						if (content) {
							content.style.marginLeft = content.oldMarginLeft;
                            content.style.marginTop = content.oldMarginTop;
                            content.style.marginBottom = content.oldMarginBottom;
						}
						for (var j in toToggle) {
							if (toToggle[j]) { toToggle[j].style.display = ''; }
						}
						if (cac && cacOldHome){
							cacOldHome.appendChild(cac); // almost back where it was :P
                        }
						setTimeout(function(){
							GM_setValue("sidebarVisible",true);
						},200);
					}
				}

			}
		}

		// log("sideBar="+sideBar+" and content="+content);
		if (sideBar) {
			// We need to watch window for clicks below sidebar (Chrome).
			document.documentElement.addEventListener('click',toggleWikipediaSidebar,false);
		} else {
			log("Did not have sideBar "+sideBar+" or content "+content); // @todo Better to warn or error?
		}

		if (!GM_getValue("sidebarVisible",true)) {
			toggleWikipediaSidebar();
		}

		// TODO: Make a toggle button for it!

		// Fix for docs.jquery.com:
		/*
		var j = document.getElementById("jq-primaryContent");
		if (j) {
			j.style.setAttribute('display', 'block');
			j.style.setAttribute('float', 'none');
			j.style.setAttribute('width', '100%');
		}
		*/
		GM_addStyle("#jq-primaryContent { display: block; float: none; width: 100%; }");

	}



	// In case you have * in your includes, only continue for pages which have
	// "wiki" before "?" in the URL, or who have both toc and content elements.
	var isWikiPage = document.location.href.split("?")[0].match("wiki")
		|| ( document.getElementById("toc") && document.getElementById("content") );

	if (!isWikiPage){
		return;
    }


} // end doIt


// setTimeout(doIt,2000);
doIt();

})();

