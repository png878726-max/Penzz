import client from './client';

export const playlistAPI = {
  // Get all playlists
  getPlaylists: () => client.get('/playlists'),

  // Create playlist
  createPlaylist: (name, description) =>
    client.post('/playlists', { name, description }),

  // Update playlist
  updatePlaylist: (id, data) =>
    client.put(`/playlists/${id}`, data),

  // Delete playlist
  deletePlaylist: (id) =>
    client.delete(`/playlists/${id}`),

  // Add song to playlist
  addSongToPlaylist: (playlistId, songId) =>
    client.post(`/playlists/${playlistId}/songs`, { songId }),

  // Remove song from playlist
  removeSongFromPlaylist: (playlistId, songId) =>
    client.delete(`/playlists/${playlistId}/songs/${songId}`),
};

export default playlistAPI;