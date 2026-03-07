<script>
    import footerLogo from "../../assets/footer-logo.jpg";
</script>

<footer class="bg-[#3870FF] text-white px-6 py-12 md:px-12">
    <div
        class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12"
    >
        <div class="flex flex-col gap-6">
            <div class="flex items-center gap-3">
                <div
                    class="bg-white p-2 rounded-full w-16 h-16 flex items-center justify-center"
                >
                    <img src={footerLogo} alt="Logo" class="w-12 h-12" />
                </div>
                <span class="text-2xl font-bold tracking-tighter"
                    >Online-Therapy</span
                >
            </div>

            <ul class="space-y-4 text-sm opacity-90">
                <li class="flex items-center gap-3">
                    <i class="fa-solid fa-envelope w-5"></i> example@mail.com
                </li>
                <li class="flex items-center gap-3">
                    <i class="fa-solid fa-phone w-5"></i> +251912345678
                </li>
                <li class="flex items-center gap-3">
                    <i class="fa-solid fa-location-dot w-5"></i> Somewhere in the
                    World
                </li>
            </ul>
        </div>

        <div>
            <h4 class="text-xl font-bold mb-6">Quick Links</h4>
            <ul class="space-y-3 opacity-80 text-sm">
                <li><a href="/" class="hover:underline">Home</a></li>
                <li><a href="/about" class="hover:underline">About Us</a></li>
                <li>
                    <a href="/doctors" class="hover:underline">Our doctors</a>
                </li>
                <li><a href="/blogs" class="hover:underline">Blogs</a></li>
                <li>
                    <a href="/contact" class="hover:underline">Contact Us</a>
                </li>
            </ul>
        </div>

        <div>
            <h4 class="text-xl font-bold mb-6">Support & Resources</h4>
            <ul class="space-y-3 opacity-80 text-sm">
                <li><a href="/faqs" class="hover:underline">FAQs</a></li>
                <li>
                    <a href="/privacy" class="hover:underline">Privacy Policy</a
                    >
                </li>
                <li>
                    <a href="/terms" class="hover:underline"
                        >Terms & Conditions</a
                    >
                </li>
                <li><a href="/help" class="hover:underline">Help Center</a></li>
            </ul>
        </div>

        <div>
            <div class="flex gap-4">
                <a
                    href="https://facebook.com"
                    class="bg-white/20 hover:bg-white/40 p-3 rounded-full transition-all"
                >
                    <i class="fa-brands fa-facebook-f text-lg"></i>
                </a>
                <a
                    href="https://x.com"
                    class="bg-white/20 hover:bg-white/40 p-3 rounded-full transition-all"
                >
                    <i class="fa-brands fa-x-twitter text-lg"></i>
                </a>
                <a
                    href="https://linkedin.com"
                    class="bg-white/20 hover:bg-white/40 p-3 rounded-full transition-all"
                >
                    <i class="fa-brands fa-linkedin-in text-lg"></i>
                </a>
                <a
                    href="https://instagram.com"
                    class="bg-white/20 hover:bg-white/40 p-3 rounded-full transition-all"
                >
                    <i class="fa-brands fa-instagram text-lg"></i>
                </a>
            </div>
        </div>
    </div>

    <div
        class="max-w-7xl mx-auto mt-16 pt-8 border-t border-white/20 text-xs opacity-70"
    >
        <p>©2026 Online-therapy. All Rights Reserved.</p>
    </div>
</footer>
