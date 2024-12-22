// store.js
import { createStore } from 'vuex';  // Используй createStore для Vue 3

export default createStore({
  state: {
    user: null
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
      console.log(user.role);
      localStorage.setItem('user', user);
      console.log(localStorage.getItem('user'));
    },
    clearUser(state) {
      state.user = null;
      console.log('logged out');
      localStorage.removeItem('user');
    },
    restoreSession(state) {
      const user = localStorage.getItem('user');
      console.log(user);
      if (user) {
        console.log(user.role);
        state.user = user;
      }
    }
  },
  actions: {
    login({ commit }, user) {
      commit('setUser', user);
    },
    logout({ commit }) {
      commit('clearUser');
    },
    restoreSession({ commit }) {
      commit('restoreSession');
    }
  },
  getters: {
    isAuthenticated: state => !!state.user,
    isAdmin: state => state.user && state.user.role === 'admin',
    isClient: state => state.user && state.user.role === 'client'
  }
});
