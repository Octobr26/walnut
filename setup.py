import site

from setuptools import setup
from setuptools.command.develop import develop


class WalnutDevelop(develop):
    """Work around Apple Python + old pip passing --user with a blank --prefix."""

    def finalize_options(self):
        if self.user and not site.ENABLE_USER_SITE:
            site.ENABLE_USER_SITE = True
        if self.user:
            self.install_userbase = self.install_userbase or site.USER_BASE
            self.install_usersite = self.install_usersite or site.USER_SITE
        super().finalize_options()


setup(
    name="walnut",
    version="0.1.0",
    description="Offline NeetCode-150 practice CLI",
    packages=["walnut"],
    python_requires=">=3.9",
    install_requires=["rich>=13", "textual>=0.60"],
    extras_require={"tui": ["textual>=0.60"]},
    entry_points={"console_scripts": ["walnut=walnut.cli:main"]},
    cmdclass={"develop": WalnutDevelop},
)
