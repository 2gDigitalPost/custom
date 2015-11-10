"""
Module for automatically formatting and sending emails.
"""

__author__ = 'topher.hughes'
__date__ = '10/09/2015'

import os
import string
import common_tools.utils as ctu

DEFAULT_TEMPLATE = r'/opt/spt/custom/formatted_emailer/fill_in_template.html'
EMAIL_HTML_DIR = r'/var/www/html/formatted_emails/'
SEND_EMAIL_COMMAND = r'/opt/spt/custom/formatted_emailer/default_emailer.php'


class SafeFormatter(string.Formatter):
    """
    A formatter class that skips missing or invalid kwargs.
    """
    def _vformat(self, format_string, args, kwargs, used_args, recursion_depth):
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result = []
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):

            # output the literal text
            if literal_text:
                result.append(literal_text)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do
                #  the formatting

                # given the field_name, find the object it references
                #  and the argument it came from
                try:
                    obj, arg_used = self.get_field(field_name, args, kwargs)
                except KeyError:
                    arg_used = field_name
                    obj = '{' + field_name + '}'
                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)

                # expand the format spec, if needed
                format_spec = self._vformat(format_spec, args, kwargs,
                                            used_args, recursion_depth-1)

                # format the object and append to the result
                try:
                    formatted = self.format_field(obj, format_spec)
                except ValueError:
                    spec = ':' + format_spec if format_spec else ''
                    formatted = '{' + field_name + spec + '}'
                result.append(formatted)

        return ''.join(result)


def safe_format_string(format_string, keyword_dict):
    """Safely formats a string with the given dictionary of keyword arguments.
    If a keyword in the format string is not found in the dictionary,
    it will simply be skipped. This is intended to format emails
    while keeping the css in tact. For example:

    safe_format_string('Hello {name}, here is a missing {keyword}.', {'name': 'Crono'})
    > 'Hello Crono, here is a missing {keyword}.'

    :param format_string: a string with keyword arguments
    :param keyword_dict: a dictionary to format the string with
    :return: a safely formatted string
    """
    return SafeFormatter().format(format_string, **keyword_dict)


def write_email_file(email_html, email_file_name):
    """Writes the email html to a file, creating the directory if necessary.

    :param email_html: formatted email as a string
    :param email_file_name: the name of the email file
    :return: a path to the html file
    """
    email_path = os.path.join(EMAIL_HTML_DIR, email_file_name)
    directory, file_name = os.path.split(email_path)
    if not os.path.isdir(directory):
        os.mkdir(directory)

    file_name, extension = os.path.splitext(file_name)
    counter = 0
    while os.path.exists(email_path):
        incremented_file_name = '{0}_{1}{2}'.format(file_name, str(counter), extension)
        email_path = os.path.join(directory, incremented_file_name)
        counter += 1

    with open(email_path, 'w') as f:
        f.write(email_html)

    return email_path


def send_email(template=DEFAULT_TEMPLATE, email_data=None, email_file_name='temp_email.html',
               attachments=None, server=None):
    """Formats an email template, saves the file as html, and sends it.
    The data should contain: to_email, from_email, subject, and message

    :param template: a path to a template file
    :param email_data: dictionary of email data
    :param email_file_name: file name for temp html file
        Note: the file name may contain subdirectories,
        all email html files will be in /var/www/html/formatted_emails/
    :param attachments: a list of file paths to attach to the email
    :param server: a TacticServerStub object used to get any misc data
    :return:
    """
    if not email_data:
        email_data = {}
    if not attachments:
        attachments = []

    if not os.path.exists(template):
        raise Exception('Email template not found: {0}'.format(template))

    # fill in default email data, fix message characters
    email_data['to_email'] = email_data.get('to_email', 'TacticDebug@2gdigital.com')
    email_data['from_email'] = email_data.get('from_email', 'TacticDebug@2gdigital.com')
    default_name = email_data['from_email'].split('@')[0].replace('.', ' ').title()
    email_data['from_name'] = email_data.get('from_name', default_name)
    email_data['subject'] = email_data.get('subject', 'No Subject')
    email_data['message'] = ctu.fix_message_characters(email_data.get('message', 'No message'))

    if server:
        # This will be None by default
        override = ctu.get_project_setting('override_to_email', server=server)
        if override == 'True':
            email_data['to_email'] = 'TacticDebug@2gdigital.com'
            email_data['ccs'] = ''

    with open(template, 'r') as f:
        email_html = f.read()
    formatted_email = safe_format_string(email_html, email_data)
    for attachment in attachments:
        # This attachment keyword has to be something that won't likely be typed by a user
        formatted_email += '\n@ACHM3NT:{0}'.format(attachment)
    email_file_path = write_email_file(formatted_email, email_file_name)

    args = [SEND_EMAIL_COMMAND, email_file_path, email_data['to_email'], email_data['from_email'],
            email_data['from_name'], email_data['subject'], email_data.get('ccs', '').replace(';', '#Xs*')]
    command = "php {0} '''{1}''' '''{2}''' '''{3}''' '''{4}''' '''{5}''' '''{6}'''".format(*args)
    print command
    os.system(command)
