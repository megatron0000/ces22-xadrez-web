(function($) {
    $.fn.hasScrollBar = function() {
        console.log(this.get(0).scrollHeight, this.innerHeight());
        return this.get(0) ? this.get(0).scrollHeight > 5 + this.innerHeight() : false;
    }
})(jQuery);

class MessageUI {
    constructor(element_selector) {
        this.__direction_append = 'left';
        this.__direction_prepend = 'right';
        /**
         * @type {jQuery}
         * @private
         */
        this.__container = $(element_selector);
        this.__onscrolltop = function () {};

        // event handler for scroll to the top
        this.__container.scroll(function () {
            if (this.__container.scrollTop() === 0) {
                this.__onscrolltop();
            }
        }.bind(this));

        this.__listeners = [];
    }


    __put_interval(element) {
        element.__message_listener = setInterval(function () {
            element.find('div div small').prettyDate();
        }, 10 * 1000);
    }

    __remove_interval(element) {
        if (element.__message_listener) {
            clearInterval(element.__message_listener);
            delete element.__message_listener;
        }
    }

    __reset_directions() {
        this.__direction_append = 'left';
        this.__direction_prepend = 'right';
    }

    __switch_direction(is_append) {
        var value = is_append ? '__direction_append' : '__direction_prepend';
        this[value] = {
            'right': 'left',
            'left': 'right'
        }[this[value]];
    }

    __get_msg_template(message, username, date, is_append) {
        var msg_li = $(
            `
          <li class="left clearfix">
            <span class="chat-img float-${is_append ? this.__direction_append : this.__direction_prepend}"
                  style="width:50px; height:50px; background-color: #${str2color(username)}; 
                  display: flex; align-items: center; justify-content: center; color: white">
                  ${username.substr(0, 3).toUpperCase()}</span>
            <div class="chat-body clearfix">
              <div class="header">
                <strong class="primary-font">${username}</strong>
                <small class="float-right text-muted" title="${date}">
                  ${date}
                </small>
              </div>
              <p>
                ${message}
              </p>
            </div>
          </li>
          `
        );
        msg_li.find('div div small').prettyDate();
        this.__switch_direction(is_append);
        return msg_li;
    }

    insert_end(message, username, date) {
        var msg_li = this.__get_msg_template(message, username, date, true);
        this.__put_interval(msg_li);
        this.__container.append(msg_li);
    }

    insert_start(message, username, date) {
        var msg_li = this.__get_msg_template(message, username, date, false);
        this.__put_interval(msg_li);
        this.__container.prepend(msg_li);
        // avoid scrolling
        this.__container.scrollTop(msg_li.outerHeight(true) + this.__container.scrollTop());
    }

    insert_start_element(element, permit_scrolling) {
        this.__container.prepend(element);
        // avoid scrolling
        if (!permit_scrolling) {
            this.__container.scrollTop(element.outerHeight(true) + this.__container.scrollTop());
        }
    }

    insert_end_element(element) {
        this.__container.append(element);
    }

    remove_start(should_scroll_start) {
        var el = this.__container.children(':first-child');
        this.__remove_interval(el);
        el.remove();
        if (should_scroll_start) {
            this.scroll_start();
        }
    }

    remove_end() {
        var el = this.__container.children(':last-child');
        this.__remove_interval(el);
        el.remove();
    }

    get_start() {
        return this.__container.find('>:first-child');
    }

    clear() {
        this.__container.empty();
        this.__reset_directions();
        for (var listener in this.__listeners) {
            clearInterval(listener);
        }
        this.__listeners = [];
    }

    is_scrolled_end() {
        var elem = this.__container[0];
        return 0 == elem.scrollHeight - elem.scrollTop - elem.clientHeight;
    }

    scroll_end() {
        this.__container.scrollTop(this.__container[0].scrollHeight - this.__container[0].clientHeight);
    }

    scroll_start() {
        this.__container.scrollTop(0);
    }

    is_scrollable() {
        return this.__container.hasScrollBar();
    }

    onscrolltop(callback) {
        this.__onscrolltop = callback;
    }

    mark_inactive() {
        this.__container.addClass('chat-inactive');
    }

    mark_active() {
        this.__container.removeClass('chat-inactive');
    }


}

class OnlineUsers {
    constructor(element_selector) {
        this.__container = $(element_selector);
        this.__mapping = {};
    }

    /**
     * Avoids duplicates automatically
     */
    insert(username) {
        // duplicate avoidance
        if (this.__mapping[username]) {
            return;
        }

        var el = $(
            `
            <tr>
              <td><span class="chat-img float-left"
                        style="width:50px; height:50px; background-color: #${str2color(username)}; display: flex; align-items: center; justify-content: center; color: white">${username.substr(0, 3).toUpperCase()}</span></td>
              <td style="vertical-align: middle; text-align:center"><strong>${username}</strong></td>
            </tr>
          `
        );
        this.__container.append(el);
        this.__mapping[username] = el;
    }

    remove(username) {
        if (!this.__mapping[username]) {
            return;
        }
        this.__mapping[username].remove();
        delete this.__mapping[username];
    }

    clear() {
        this.__container.empty();
        this.__mapping = {};
    }
}