import { writable } from "svelte/store";

const sidebarOpen = writable(false);

const openSidebar = () => sidebarOpen.set(true);
const closeSidebar = () => sidebarOpen.set(false);
const toggleSidebar = () => sidebarOpen.update((value) => !value);

export { sidebarOpen, openSidebar, closeSidebar, toggleSidebar };
