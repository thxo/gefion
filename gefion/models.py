# -*- coding: utf-8 -*-
"""SQLAlchemy ORM mdoels."""

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Table, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

contact_association = Table('contactassociations', Base.metadata, Column(
    'monitor_id', Integer, ForeignKey('monitors.id')), Column(
        'contact_id', Integer, ForeignKey('contacts.id')))


class Monitor(Base):
    """Scheduled monitoring tasks.

    Attributes:
        id (Column(Integer)): Auto-incremental ID.
        name (Column(String)): User-friendly identifying name.
        unique_id (Column(String)): Version UUID, updated when arguments are.
        check (Column(String)): Type of check. Use names in name_maps.
        arguments (Column(String)): JSON-ed dict, information passed onto
            Notifiers.
        worker (Column(String)): Name of the worker. Use names assigned in the
            config file.
        frequency (Column(Integer)): In minutes.
        last_availability (Column(Boolean)): Latest availability.
        last_message (Column(String)): Latest message.
        last_updated (Column((DateTime)): Last time check was run.
        contacts (relationship): Contacts that should be notified.
    """

    __tablename__ = 'monitors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    unique_id = Column(String)
    check = Column(String)  # ex. `port`.
    arguments = Column(String)
    worker = Column(String)
    frequency = Column(Integer)
    last_availability = Column(Boolean)
    last_message = Column(String)
    last_updated = Column(DateTime, default=func.now())
    contacts = relationship('Contact',
                            secondary=contact_association,
                            backref='monitors')

    @property
    def api_serialised(self):
        """Return serialisable data for API monitor assignments."""
        return {'id': self.id,
                'name': self.name,
                'unique_id': self.unique_id,
                'check': self.check,
                'arguments': self.arguments,
                'worker': self.worker,
                'frequency': self.frequency}


class Contact(Base):
    """Contacts that can be notified.

    Attributes:
        id (Column(Integer)): Auto-incremental ID.
        name (Column(String)): User-friendly identifying name.
        notifier (Column(String)): Type of notifier. Use names in name_maps.
        destination (Column(String)): Destination of message, ex. phone numbers
            or chat IDs.
    """

    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    notifier = Column(String)  # ex `telegram`.
    destination = Column(String)
