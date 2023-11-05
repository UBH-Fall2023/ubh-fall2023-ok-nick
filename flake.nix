{
  description = "A Matrix server for anonymously communicating with UB classmates in each class section";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    yap-my-classes = pkgs.python311Packages.buildPythonPackage {
      pname = "yap_my_classes";
      version = "0.1.0";
      pyproject = true;
      src = ./.;
      buildInputs = [pkgs.matrix-synapse-unwrapped];
      pythonImportsCheck = ["yap_my_classes"];
      doCheck = false;
    };
  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [pkgs.matrix-synapse-unwrapped];
    };

    packages.${system}.default = yap-my-classes;

    nixosModules.default = {
      config,
      lib,
      pkgs,
      ...
    }: let
      cfg = config.programs.yap-my-classes;
    in {
      options.programs.yap-my-classes = {
        enable = lib.mkEnableOption "Enables yap-my-classes";
        package = lib.mkOption {
          type = lib.types.package;
          default = yap-my-classes;
        };
      };

      config = lib.mkIf cfg.enable {
        environment.systemPackages = [yap-my-classes];

        services.postgresql = {
          enable = true;
          initialScript = pkgs.writeText "synapse-init.sql" ''
            CREATE ROLE "matrix-synapse" WITH LOGIN PASSWORD 'synapse';
            CREATE DATABASE "matrix-synapse" WITH OWNER 'matrix-synapse'
              TEMPLATE template0
              LC_COLLATE = 'C'
              LC_CTYPE = 'C';
          '';
        };

        services.matrix-synapse = {
          enable = true;
          settings = {
            server_name = "localhost:8080"; # TODO: temp until domain
            # block_non_admin_invites = true; # no invites by users (maybe can enable if global public chat)

            enable_registration = true;
            enable_registration_without_verification = true;
            # disable_msisdn_registration = true; # disable phone number?
            registration_shared_secret = "test";
            # registration_requires_token = true;
            # allow_guest_access = true;

            password_config = {
              # TODO: checkout
              policy.enabled = false;
            };

            # auto_join_rooms = [""]; # TODO: global chat
            # autocreate_auto_join_rooms = true;
            # autocreate_auto_join_rooms_federated = false;
            # autocreate_auto_join_room_preset
            # auto_join_mxid_localpart

            room_prejoin_state = {
              # TODO
            };

            modules = [
              {
                module = "yap_my_classes.Navigate";
              }
            ];
          };
          log = {
            loggers."navigate".level = "DEBUG";
          };
          plugins = [
            yap-my-classes
          ];
        };
      };
    };
  };
}
