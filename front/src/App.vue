
<template>
    <div id="app">
      <!-- Отображаем текущий компонент в зависимости от маршрута -->
      <router-view></router-view>
    </div>
</template>
  
<script>
  export default {
    name: 'App',
  };
</script>
  
<style>
/* Styles visible from anywhere */
  .navigation {
    text-align: center;
    margin: 1rem;
  }

  .form-group {
    margin-bottom: 1rem;

    input, select, textarea {
      width: 100%;
      margin-bottom: 1rem;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 1rem;
    }
  }

  .white_box {
    /* max-width: 25rem; */
    padding: 2rem;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .button_blue {
    /* width: 100%; */
    background-color: var(--primary-color);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 1rem;
    cursor: pointer;

    &:hover {
      background-color: var(--primary-color-dark);
    }
  }
  .button_red {
    background-color: var(--red-color);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 1rem;
    cursor: pointer;

    &:hover {
      background-color: var(--red-color-dark);
    }
  }
  h2 {
    margin-bottom: 1rem;
    text-align: center;
    color: var(--primary-color);
  }

  p {
    margin-bottom: 1rem;
    text-align: left;
  }
</style>
  