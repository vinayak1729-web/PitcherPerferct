import React, { useState, useEffect, useRef } from 'react';
import { Search, UserPlus, Users, Send, PlusCircle, FileUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const SocialPlatform = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('all');
  const [searchResults, setSearchResults] = useState({ users: [], groups: [] });
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [newGroup, setNewGroup] = useState({ name: '', description: '' });
  const [alert, setAlert] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSearch = async () => {
    try {
      const response = await fetch(`/search?q=${searchQuery}&type=${searchType}`);
      const data = await response.json();
      if (data.success) {
        setSearchResults(data.results);
      }
    } catch (error) {
      showAlert('Error performing search', 'error');
    }
  };

  const handleSendFriendRequest = async (username) => {
    try {
      const response = await fetch('/send_friend_request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
      });
      const data = await response.json();
      if (data.success) {
        showAlert('Friend request sent successfully!', 'success');
      } else {
        showAlert(data.message, 'error');
      }
    } catch (error) {
      showAlert('Error sending friend request', 'error');
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      const response = await fetch('/join_group', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group_id: groupId })
      });
      const data = await response.json();
      if (data.success) {
        showAlert('Successfully joined group!', 'success');
      } else {
        showAlert(data.message, 'error');
      }
    } catch (error) {
      showAlert('Error joining group', 'error');
    }
  };

  const handleCreateGroup = async () => {
    try {
      const response = await fetch('/create_group', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newGroup)
      });
      const data = await response.json();
      if (data.success) {
        showAlert('Group created successfully!', 'success');
        setShowCreateGroup(false);
        setNewGroup({ name: '', description: '' });
      }
    } catch (error) {
      showAlert('Error creating group', 'error');
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() && !fileInputRef.current?.files?.length) return;

    try {
      if (fileInputRef.current?.files?.length) {
        const formData = new FormData();
        formData.append('file', fileInputRef.current.files[0]);
        formData.append('recipient', selectedChat);
        formData.append('type', 'user');

        const response = await fetch('/send_file', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (data.success) {
          setMessages([...messages, data.message]);
        }
        fileInputRef.current.value = '';
      }

      if (newMessage.trim()) {
        const response = await fetch('/send_message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            recipient: selectedChat,
            content: newMessage
          })
        });
        const data = await response.json();
        if (data.success) {
          setMessages([...messages, data.message]);
          setNewMessage('');
        }
      }
    } catch (error) {
      showAlert('Error sending message', 'error');
    }
  };

  const showAlert = (message, type) => {
    setAlert({ message, type });
    setTimeout(() => setAlert(null), 3000);
  };

  const fetchMessages = async (recipient) => {
    try {
      const response = await fetch(`/messages/${recipient}`);
      const data = await response.json();
      if (data.success) {
        setMessages(data.messages);
      }
    } catch (error) {
      showAlert('Error fetching messages', 'error');
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-6xl mx-auto p-4 gap-4">
      {alert && (
        <Alert className={`${alert.type === 'error' ? 'bg-red-100' : 'bg-green-100'}`}>
          <AlertDescription>{alert.message}</AlertDescription>
        </Alert>
      )}
      
      <div className="flex gap-4 items-center">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search users or groups..."
          className="flex-1 p-2 border rounded"
        />
        <select
          value={searchType}
          onChange={(e) => setSearchType(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="all">All</option>
          <option value="users">Users</option>
          <option value="groups">Groups</option>
        </select>
        <button
          onClick={handleSearch}
          className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          <Search className="w-5 h-5" />
        </button>
        <button
          onClick={() => setShowCreateGroup(true)}
          className="p-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          <PlusCircle className="w-5 h-5" />
        </button>
      </div>

      {showCreateGroup && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Create New Group</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <input
                type="text"
                value={newGroup.name}
                onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
                placeholder="Group Name"
                className="w-full p-2 border rounded"
              />
              <textarea
                value={newGroup.description}
                onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
                placeholder="Group Description"
                className="w-full p-2 border rounded"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleCreateGroup}
                  className="p-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  Create Group
                </button>
                <button
                  onClick={() => setShowCreateGroup(false)}
                  className="p-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Search Results */}
        <Card className="h-96 overflow-y-auto">
          <CardHeader>
            <CardTitle>Search Results</CardTitle>
          </CardHeader>
          <CardContent>
            {searchResults.users.length > 0 && (
              <div className="mb-4">
                <h3 className="font-bold mb-2">Users</h3>
                {searchResults.users.map(user => (
                  <div key={user.id} className="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
                    <span>{user.username}</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSendFriendRequest(user.username)}
                        className="p-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                      >
                        <UserPlus className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          setSelectedChat(user.username);
                          fetchMessages(user.username);
                        }}
                        className="p-1 bg-green-500 text-white rounded hover:bg-green-600"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {searchResults.groups.length > 0 && (
              <div>
                <h3 className="font-bold mb-2">Groups</h3>
                {searchResults.groups.map(group => (
                  <div key={group.id} className="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
                    <div>
                      <div className="font-medium">{group.name}</div>
                      <div className="text-sm text-gray-500">{group.description}</div>
                    </div>
                    <button
                      onClick={() => handleJoinGroup(group.id)}
                      className="p-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      <Users className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Chat Section */}
        {selectedChat && (
          <Card className="h-96">
            <CardHeader>
              <CardTitle>Chat with {selectedChat}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 overflow-y-auto mb-4 space-y-2">
                {messages.map(message => (
                  <div
                    key={message.id}
                    className={`p-2 rounded max-w-[80%] ${
                      message.sender === selectedChat
                        ? 'bg-gray-100 ml-0'
                        : 'bg-blue-100 ml-auto'
                    }`}
                  >
                    {message.type === 'file' ? (
                      <a
                        href={`/download/${message.file.path}`}
                        className="text-blue-500 hover:underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        📎 {message.file.name}
                      </a>
                    ) : (
                      message.content
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 p-2 border rounded"
                />
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept=".pdf,.doc,.docx,.txt,image/*"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  <FileUp className="w-5 h-5" />
                </button>
                <button
                  onClick={handleSendMessage}
                  className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default SocialPlatform;